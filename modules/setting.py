from tornado import gen
from tornado.log import app_log as log
from munch import munchify
import pymysql
from settings import pool


class SettingModule(object):
    """
    设置表相关操作
    """
    # 添加配置项
    @gen.coroutine
    def add_setting(self, pid, s_type, name, value, status=1, sort=1):
        sql = """INSERT INTO t_settings (`project`, `type`, `name`, `value`, `status`, `sort`)
        VALUE (%(pid)s, %(s_type)s, %(name)s, %(value)s, %(status)s, %(sort)s)"""
        with (yield pool.Connection()) as conn:
            with conn.cursor() as cursor:
                try:
                    yield cursor.execute(sql, dict(pid=pid, s_type=s_type, name=name, value=value, status=status, sort=sort))
                except pymysql.Error as e:
                    yield conn.rollback()
                    log.error('新增 {} 设置项 {} 失败#{}'.format(s_type, name, e))
                    flag, msg = False, '新增 {} 设置项 {} 失败#{}'.format(s_type, name, e)
                else:
                    yield conn.commit()
                    log.info('新增 {} 设置项 {} 成功'.format(s_type, name))
                    flag, msg = cursor.lastrowid, '新增 {} 设置项 {} 成功'.format(s_type, name)
        return flag, msg

    # 删除配置项
    @gen.coroutine
    def delete_setting(self, sid):
        setting = yield self.get_setting_by_id(sid=sid)
        if setting:
            sql = 'DELETE FROM t_settings WHERE id=%(sid)s'
            tx = yield pool.begin()
            try:
                yield tx.execute(sql, dict(sid=sid))
            except pymysql.Error as e:
                yield tx.rollback()
                log.error('删除 {} 设置项 {} 失败#{}'.format(setting.type, setting.name, e))
                flag, msg = False, '删除 {} 设置项 {} 失败#{}'.format(setting.type, setting.name, e)
            else:
                yield tx.commit()
                log.info('删除 {} 设置项 {} 成功'.format(setting.type, setting.name))
                flag, msg = True, '删除 {} 设置项 {} 成功'.format(setting.type, setting.name)
        else:
            flag, msg = False, '不存在指定的设置项'
        return flag, msg

    # 按类型批量删除配置项
    @gen.coroutine
    def delete_settings_list(self, s_type, status=None):
        setting = yield self.get_settings_list(s_type=s_type, status=status)
        if setting:
            if status:
                sql = 'DELETE FROM t_settings WHERE type=%(s_type)s AND status=%(status)s'
            else:
                sql = 'DELETE FROM t_settings WHERE type=%(s_type)s'
            tx = yield pool.begin()
            try:
                yield tx.execute(sql, dict(s_type=s_type, status=status))
            except pymysql.Error as e:
                yield tx.rollback()
                log.error('批量删除设置项 {} 失败#{}'.format(s_type, e))
                flag, msg = False, '批量删除设置项 {} 失败#{}'.format(s_type, e)
            else:
                yield tx.commit()
                log.info('批量删除设置项 {} 成功'.format(s_type))
                flag, msg = True, '批量删除设置项 {} 成功'.format(s_type)
        else:
            flag, msg = False, '不存在指定的设置项'
        return flag, msg

    # 编辑配置项
    @gen.coroutine
    def edit_setting(self, sid, status=None, name=None, value=None, sort=None):
        update = []
        param = dict(sid=sid)
        if status is not None:
            update.append('s.status=%(status)s')
            param['status'] = status
        if name is not None:
            update.append("s.name=%(name)s")
            param['name'] = name
        if value is not None:
            update.append("s.value=%(value)s")
            param['value'] = value
        if sort is not None:
            update.append('s.sort=%(sort)s')
            param['sort'] = sort
        setting = yield self.get_setting_by_id(sid=sid)
        if update and setting:
            sql = 'UPDATE t_settings s SET {} WHERE id=%(sid)s'.format(', '.join(update))
            tx = yield pool.begin()
            try:
                yield tx.execute(sql, param)
            except pymysql.Error as e:
                yield tx.rollback()
                log.error('更新 {} 配置项 {} 失败#{}'.format(setting.type, setting.name, e))
                flag, msg = False, '更新 {} 配置项 {} 失败#{}'.format(setting.type, setting.name, e)
            else:
                yield tx.commit()
                log.info('更新 {} 配置项 {} 成功'.format(setting.type, setting.name))
                flag, msg = True, '更新 {} 配置项 {} 成功'.format(setting.type, setting.name)
            return flag, msg
        else:
            log.error('没有指定编辑的配置项')
            return False, '没有指定编辑的配置项'

    # 通过条件获取配置项列表
    @gen.coroutine
    def get_settings_list(self, pid=None, name=None, s_type=None, user=None,
                          status=None, pj_status=None, page=1, limit=10):
        sql = """
            SELECT s.id, s.project project_id, s.type, s.name, s.value, s.status, p.name project_name, s.sort
            FROM t_settings s JOIN t_projects p ON s.project=p.id
            """
        sql_count = 'SELECT COUNT(*) count FROM t_settings s JOIN t_projects p ON s.project=p.id'
        where = []
        param = dict()
        if pid is not None:
            where.append('s.project=%(pid)s')
            param['pid'] = pid
        if name is not None:
            where.append("s.name=%(name)s")
            param['name'] = name
        if s_type is not None:
            where.append("s.type=%(s_type)s")
            param['s_type'] = s_type
        if user is not None:
            where.append("p.user LIKE %(user)s")
            param['user'] = '%{}%'.format(user)
        if status is not None:
            where.append('s.status=%(status)s')
            param['status'] = status
        if pj_status is not None:
            where.append('p.status=%(pj_status)s')
            param['pj_status'] = pj_status
        if where:
            sql += ' WHERE {}'.format(' AND '.join(where))
            sql_count += ' WHERE {}'.format(' AND '.join(where))
        if s_type == 'report':
            sql += ' ORDER BY s.name DESC'
        elif s_type == 'job':
            sql += ' ORDER BY s.sort, s.status, s.name DESC'
        elif s_type == 'host':
            sql += ' ORDER BY s.project DESC, s.name DESC, s.value, s.status'
        else:
            sql += ' ORDER BY s.sort, s.status, s.project DESC, s.name DESC, s.value'
        if limit is not None:
            offset = (page - 1) * limit
            sql += ' LIMIT {},{}'.format(offset, limit)
        cursor = yield pool.execute(sql, param)
        result = cursor.fetchall()
        cursor = yield pool.execute(sql_count, param)
        total = cursor.fetchone()
        cursor.close()
        return munchify(result), munchify(total).count

    # 通过id获取配置项
    @gen.coroutine
    def get_setting_by_id(self, sid):
        sql = """
            SELECT s.id, s.project project_id, s.type, s.name, s.value, s.status, p.name project_name, s.sort
            FROM t_settings s JOIN t_projects p ON s.project=p.id WHERE s.id=%(sid)s
            """
        cursor = yield pool.execute(sql, dict(sid=sid))
        result = cursor.fetchone()
        cursor.close()
        return munchify(result)

    # 通过多个id获取配置项列表
    @gen.coroutine
    def get_settings_by_ids(self, sids):
        if sids and isinstance(sids, list):
            param = dict()
            ins = ''
            for i in range(len(sids)):
                param['id{}'.format(i)] = sids[i]
                ins += '%(id{})s,'.format(i)
            sql = """
                SELECT s.id, s.project project_id, s.type, s.name, s.value, s.status, p.name project_name, s.sort
                FROM t_settings s JOIN t_projects p ON s.project=p.id WHERE s.id in ({}) ORDER BY s.sort
                """.format(ins[:-1])
            cursor = yield pool.execute(sql, param)
            result = cursor.fetchall()
            cursor.close()
            return munchify(result)
        else:
            return []

    # 通过区间搜索配置
    @gen.coroutine
    def get_settings_by_range(self, pid, s_type, sort, range_col='name', start='', end=''):
        sql = """
            SELECT s.id, s.project project_id, s.type, s.name, s.value, s.status, p.name project_name, s.sort
            FROM t_settings s JOIN t_projects p ON s.project=p.id
            """
        where = []
        param = dict()
        if pid is not None:
            where.append('s.project=%(pid)s')
            param['pid'] = pid
        if s_type is not None:
            where.append("s.type=%(s_type)s")
            param['s_type'] = s_type
        if sort is not None:
            where.append("s.sort=%(sort)s")
            param['sort'] = sort
        if range_col == 'name':
            where.append('s.name BETWEEN %(start)s AND %(end)s')
        else:
            where.append('s.value BETWEEN %(start)s AND %(end)s')
        param['start'] = start
        param['end'] = end
        if where:
            sql += ' WHERE {}'.format(' AND '.join(where))
        cursor = yield pool.execute(sql, param)
        result = cursor.fetchall()
        cursor.close()
        return munchify(result)
