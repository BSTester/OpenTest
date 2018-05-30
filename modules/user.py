import time
from settings import pool
from functions.common import CommonFunction
from tornado.log import app_log as log
from tornado import gen
from munch import munchify
import pymysql


class UserModule(object):
    """
    用户表相关操作
    """
    def __init__(self):
        self.common_func = CommonFunction()

    # 获取用户信息
    @gen.coroutine
    def get_user_info(self, email_or_username, status=None):
        sql = "SELECT * FROM t_users u WHERE (u.email=%(user)s OR u.username=%(user)s)"
        param = dict(user=email_or_username)
        if status is not None:
            sql += ' AND u.status=%(status)s'
            param['status'] = status
        cursor = yield pool.execute(sql, param)
        result = cursor.fetchone()
        cursor.close()
        return munchify(result)

    # 通过user_id获取用户信息
    @gen.coroutine
    def get_users_info_by_ids(self, ids, status=None):
        if ids and isinstance(ids, list):
            param = dict()
            ins = ''
            for i in range(len(ids)):
                param['id{}'.format(i)] = ids[i]
                ins += '%(id{})s,'.format(i)
            sql = 'SELECT * FROM t_users u WHERE u.id in ({})'.format(ins[:-1])
            if status is not None:
                sql += ' AND status=%(status)s'
                param['status'] = status
            sql += ' ORDER BY u.role'
            cursor = yield pool.execute(sql, param)
            result = cursor.fetchall()
            cursor.close()
            return munchify(result)
        else:
            return []

    # 获取用户列表
    @gen.coroutine
    def get_users_list(self, page=1, limit=10, status=None):
        sql = 'SELECT * FROM t_users u'
        sql_count = 'SELECT COUNT(*) count FROM t_users u'
        if status is not None:
            sql += ' WHERE u.status=%(status)s'
            sql_count += ' WHERE u.status=%(status)s'
        sql += ' ORDER BY u.role'
        if limit is not None:
            offset = (page - 1) * limit
            sql += ' LIMIT {},{}'.format(offset, limit)
        cursor = yield pool.execute(sql, dict(status=status))
        result = cursor.fetchall()
        cursor = yield pool.execute(sql_count, dict(status=status))
        total = cursor.fetchone()
        cursor.close()
        return munchify(result), munchify(total).count

    # 注册用户
    @gen.coroutine
    def register_user(self, email, password):
        register_time = time.strftime('%Y-%m-%d %H:%M:%S')
        password = self.common_func.encode_password(password)
        cursor = yield pool.execute('SELECT COUNT(*) count FROM t_users')
        total = munchify(cursor.fetchone())
        if total.count == 0:
            role = 0
        else:
            role = 2
        username = '{}_{}'.format(email.split('@')[0], str(int(time.time()*1000)))
        sql = """
        INSERT INTO t_users (username, email, password, registerTime, lastLoginTime, role)
        VALUE(%(username)s, %(email)s, %(password)s, %(registerTime)s, %(lastLoginTime)s, %(role)s)
        """
        user = yield self.get_user_info(email_or_username=email)
        if not user:
            with (yield pool.Connection()) as conn:
                with conn.cursor() as cursor:
                    try:
                        yield cursor.execute(sql, dict(username=username, email=email, password=password,
                                                       registerTime=register_time, lastLoginTime=register_time, role=role))
                    except pymysql.Error as e:
                        yield conn.rollback()
                        log.error('注册用户失败#{}'.format(e))
                        flag, msg = False, '注册用户失败#{}'.format(e)
                    else:
                        yield conn.commit()
                        log.info('注册用户成功')
                        flag, msg = cursor.lastrowid, '注册用户成功'
        else:
            log.error('该用户已存在, 请更换注册邮箱')
            flag, msg = False, '该用户已存在, 请更换注册邮箱'
        return flag, msg

    # 编辑用户
    @gen.coroutine
    def edit_user(self, email, password=None, username=None, realname=None, last_login_time=None,
                  role=None, status=None):
        user = yield self.get_user_info(email)
        if user:
            update = []
            param = dict(email=user.email)
            if password is not None:
                update.append("password=%(password)s")
                param['password'] = self.common_func.encode_password(password)
            if username is not None:
                sql = "SELECT username FROM t_users u WHERE u.email != %(email)s AND u.username = %(username)s"
                param['username'] = username
                cursor = yield pool.execute(sql, param)
                user_info = cursor.fetchone()
                if user_info:
                    log.error('用户名 {} 已存在'.format(username))
                    return False, '用户名 {} 已存在'.format(username)
                else:
                    update.append("username=%(username)s")
            if realname is not None:
                update.append("realname=%(realname)s")
                param['realname'] = realname
            if last_login_time is not None:
                update.append("lastLoginTime=%(lastLoginTime)s")
                param['lastLoginTime'] = last_login_time
            if role is not None:
                update.append('role=%(role)s')
                param['role'] = role
            if status is not None:
                update.append('status=%(status)s')
                param['status'] = status
            if update:
                sql = "UPDATE t_users SET {} WHERE email=%(email)s".format(', '.join(update))
                tx = yield pool.begin()
                try:
                    yield tx.execute(sql, param)
                except pymysql.Error as e:
                    yield tx.rollback()
                    log.error('编辑用户失败#{}'.format(e))
                    flag, msg = False, '用户 {} 资料修改失败'.format(email)
                else:
                    yield tx.commit()
                    log.info('用户 {} 资料修改成功'.format(email))
                    flag, msg = True, '用户 {} 资料修改成功'.format(email)
                return flag, msg
            else:
                log.error('没有可更新的项')
                return False, '没有可更新的项'
        else:
            log.error('没有可编辑的用户#{}'.format(email))
            return False, '没有可编辑的用户#{}'.format(email)
