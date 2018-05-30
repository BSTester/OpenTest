from settings import pool
from tornado.log import app_log as log
from tornado import gen
import pymysql
from munch import munchify


class OptionModule(object):
    """
    系统配置表相关操作
    """
    # 新增系统配置
    @gen.coroutine
    def add_option(self, name, value):
        option = yield self.get_option(name=name)
        if not option:
            sql = "INSERT INTO t_options (`name`, `value`) VALUE (%(name)s, %(value)s)"
            with (yield pool.Connection()) as conn:
                with conn.cursor() as cursor:
                    try:
                        yield cursor.execute(sql, dict(name=name, value=value))
                    except pymysql.Error as e:
                        yield conn.rollback()
                        log.error('添加系统配置失败#{}'.format(e))
                        flag, msg = False, '添加系统配置失败#{}'.format(e)
                    else:
                        yield conn.commit()
                        log.info('添加系统配置成功')
                        flag, msg = cursor.lastrowid, '添加系统配置成功'
        else:
            log.error('系统配置已存在, 无法新增')
            flag, msg = False, '系统配置已存在, 无法新增'
        return flag, msg

    # 删除系统配置
    @gen.coroutine
    def delete_option(self, name=None, oid=None):
        where = []
        param = dict()
        if name is not None:
            where.append("name=%(name)s")
            param['name'] = name
        if oid is not None:
            where.append("id=%(oid)s")
            param['oid'] = oid
        if where:
            sql = "DELETE FROM t_options WHERE {}".format(' AND '.join(where))
            tx = yield pool.begin()
            try:
                yield tx.execute(sql, param)
            except pymysql.Error as e:
                yield tx.rollback()
                log.error('删除系统配置失败#{}'.format(e))
                flag, msg = False, '删除系统配置失败#{}'.format(e)
            else:
                yield tx.commit()
                log.info('删除系统配置成功')
                flag, msg = True, '删除系统配置成功'
        else:
            log.error('没有指定系统配置, 删除失败')
            flag, msg = False, '没有指定系统配置, 删除失败'
        return flag, msg

    # 编辑系统配置
    @gen.coroutine
    def edit_option(self, value, name=None, oid=None):
        where = []
        param = dict(value=value)
        if name is not None:
            where.append("name=%(name)s")
            param['name'] = name
        elif oid is not None:
            where.append("id=%(oid)s")
            param['oid'] = oid
        else:
            log.error('参数不对, 编辑系统配置失败')
            return False, '参数不对, 编辑系统配置失败'
        option = yield self.get_option(name=name, oid=oid)
        if where and option:
            sql = "UPDATE t_options o SET value=%(value)s WHERE {}".format(' AND '.join(where))
            tx = yield pool.begin()
            try:
                yield tx.execute(sql, param)
            except pymysql.Error as e:
                yield tx.rollback()
                log.error('系统配置 {} 编辑失败#{}'.format(option.name, e))
                flag, msg = False, '系统配置 {} 编辑失败#{}'.format(option.name, e)
            else:
                yield tx.commit()
                log.info('系统配置 {} 编辑成功'.format(option.name))
                flag, msg = True, '系统配置 {} 编辑成功'.format(option.name)
        else:
            log.error('没有可编辑的系统配置')
            flag, msg = False, '没有可编辑的系统配置'
        return flag, msg

    # 获取系统配置
    @gen.coroutine
    def get_option(self, name=None, oid=None):
        where = []
        param = dict()
        if name is not None:
            where.append("o.name=%(name)s")
            param['name'] = name
        if oid is not None:
            where.append("o.id=%(oid)s")
            param['oid'] = oid
        if where:
            sql = "SELECT * FROM t_options o WHERE {}".format(' AND '.join(where))
            cursor = yield pool.execute(sql, param)
            result = cursor.fetchone()
            cursor.close()
            return munchify(result)
        else:
            log.error('参数不对, 获取系统配置失败')
            return None

    # 获取所有系统配置
    @gen.coroutine
    def get_options_list(self):
        sql = "SELECT * FROM t_options"
        cursor = yield pool.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return munchify(result)
