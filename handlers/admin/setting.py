from tornado.web import escape
from tornado import gen
from tornado.log import app_log as log
from munch import munchify
from functions.custom import config
from handlers.common import BaseHandler, authenticated_async
from modules.testing import TestingModule
from handlers.admin.api import AddLogs
import math
import json


# 设置操作类
class SettingHandler(BaseHandler):
    @authenticated_async
    @gen.coroutine
    def get(self, op='project', pid=0, page=1, limit=10):
        if not isinstance(limit, int):
            limit = int(limit)
        else:
            limit = limit if self.limit == '' else int(self.limit)
        project_list = yield self.project.get_projects_by_user(user=self.current_user.email, status=1)
        page = 1 if int(page) <= 0 else int(page)
        pid = 0 if int(pid) < 0 else int(pid)
        if op == 'project':
            lists, total = yield self.project.get_projects_list(page=page, limit=limit)
            if lists:
                projects = []
                for row in lists:
                    project = dict()
                    project['id'] = row.id
                    project['name'] = row.name
                    project['user'] = self.__get_setting_project_user_email(row.user)
                    project['status'] = row.status
                    projects.append(munchify(project))
                lists = projects
            total_page = int(math.ceil(total / limit))
        elif op == 'host':
            lists, total = yield self.setting.get_settings_list(s_type='host', page=page, limit=limit,
                                                                user=self.current_user.email, pj_status=1)
            if pid != 0:
                lists, total = yield self.setting.get_settings_list(
                    pid=pid, s_type='host', user=self.current_user.email, pj_status=1, limit=limit, page=page)
            if self.current_user.role != 2:
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
                lists, total = yield self.setting.get_settings_list(s_type='host', page=page, limit=limit)
                if pid != 0:
                    lists, total = yield self.setting.get_settings_list(
                        pid=pid, s_type='host', pj_status=1, limit=limit, page=page)
            total_page = int(math.ceil(total / limit))
        elif op == 'interface':
            lists, total = yield self.setting.get_settings_list(
                s_type='url', page=page, limit=limit, user=self.current_user.email, pj_status=1)
            if pid != 0:
                lists, total = yield self.setting.get_settings_list(
                    pid=pid, s_type='url', user=self.current_user.email, pj_status=1, limit=limit, page=page)
            if self.current_user.role != 2:
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
                lists, total = yield self.setting.get_settings_list(s_type='url', page=page, limit=limit)
                if pid != 0:
                    lists, total = yield self.setting.get_settings_list(
                        pid=pid, s_type='url', pj_status=1, limit=limit, page=page)
            lists = self.__get_setting_interface(lists)
            total_page = int(math.ceil(total / limit))
        elif op == 'crypt':
            lists, total = yield self.setting.get_settings_list(
                s_type='crypt', page=page, limit=limit, user=self.current_user.email, pj_status=1)
            if self.current_user.role != 2:
                project_list, total = yield self.project.get_projects_list(limit=None, status=1)
                lists, total = yield self.setting.get_settings_list(s_type='crypt', page=page, limit=limit)
            lists = self.__get_setting_crypt(lists)
            total_page = int(math.ceil(total / limit))
        else:
            self.redirect('/admin/setting')
            return
        argv = dict(title='设置', op=op, lists=lists, page=page, limit=limit, pid=pid, total_page=total_page,
                    project_list=project_list, encrypt=config.encrypt, decrypt=config.decrypt,
                    customs_func=config.customs_func)
        argv = dict(self.argv, **argv)
        total_page = 1 if total_page <= 0 else total_page
        if total_page < page:
            self.redirect('/admin/setting/{}/{}/{}/{}'.format(op, pid, total_page, limit))
            return
        else:
            self.render('admin/setting.html', **argv)

    # 获取项目权限用户
    def __get_setting_project_user_email(self, users):
        if users:
            user = ''
            for row in json.loads(users):
                user += '{};\t'.format(json.loads(row)['username'])
            return user
        else:
            return ''

    # 获取接口配置拆分接口链接
    def __get_setting_interface(self, interface):
        setting = dict()
        lists = []
        for row in interface:
            value = json.loads(row.value)
            setting['id'] = row.id
            setting['type'] = row.type
            setting['project_id'] = row.project_id
            setting['project_name'] = row.project_name
            setting['name'] = row.name
            setting['value'] = self.common_func.url_split(value['url'])
            setting['label'] = value['label']
            setting['key'] = value['key']
            setting['status'] = row.status
            lists.append(munchify(setting))
        return lists

    # 获取所有项目加解密配置
    def __get_setting_crypt(self, crypt):
        setting = dict()
        lists = []
        for row in crypt:
            setting['id'] = row.id
            setting['type'] = row.type
            setting['project_id'] = row.project_id
            setting['project_name'] = row.project_name
            setting['name'] = row.name
            setting['value'] = json.loads(row.value)
            setting['status'] = row.status
            lists.append(munchify(setting))
        return lists

    @authenticated_async
    @gen.coroutine
    def post(self, op='project', do='add'):
        if op == 'project':
            yield self.__setting_project(do)
        elif op == 'host':
            yield self.__setting_host(do)
        elif op == 'interface':
            yield self.__setting_interface(do)
        elif op == 'crypt':
            yield self.__setting_crypt(do)
        else:
            self.redirect('/admin/setting')

    # 项目配置
    @gen.coroutine
    def __setting_project(self, do=''):
        add_logs = AddLogs(operate_ip=self.request.remote_ip)
        add_logs.add_logs()
        if do == 'add':
            name = self.get_argument('project', default='')
            project = yield self.project.get_project(name)
            if project is not None or name == '':
                self.redirect('/admin/setting/project')
                return
            yield self.project.add_project(name)
            self.redirect('/admin/setting/project')
            return
        elif do == 'delete':
            pid = int(self.get_argument('id', default=0))
            s_param, total = yield self.setting.get_settings_list(pid=pid, s_type='param', limit=None)
            s_job, total = yield self.setting.get_settings_list(pid=pid, s_type='job', limit=None)
            s_log, total = yield self.setting.get_settings_list(pid=pid, s_type='log', limit=None)
            s_report, total = yield self.setting.get_settings_list(pid=pid, s_type='report', limit=None)
            try:
                for row in s_param:
                    self.setting.delete_setting(row.id)
                for row in s_job:
                    self.setting.delete_setting(row.id)
                for row in s_log:
                    self.setting.delete_setting(row.id)
                for row in s_report:
                    self.setting.delete_setting(row.id)
                result, msg = yield self.project.delete_project(pid=pid)
            except Exception as e:
                log.error(e)
                result = False
                msg = str(e)
            if result:
                msg = dict(result=True, msg='/admin/setting/project')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'update':
            pid = int(self.get_argument('pid', default=0))
            status = self.get_argument('status', default='')
            result, msg = yield self.project.edit_project(pid=pid, status=int(status))
            if result:
                msg = dict(result=True, msg='/admin/setting/project')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'getuser':
            pid = int(self.get_argument('pid', default=0))
            users, total = yield self.user.get_users_list(status=1, limit=None)
            if not users:
                msg = dict(result=False, msg="没有可选的用户")
                yield self.return_json(msg)
                return
            project = yield self.project.get_project(pid=pid)
            current_user = []
            if project.user:
                for row in json.loads(project.user):
                    current_user.append(json.loads(row))
            user_list = []
            for user in users:
                user_info = {'uid': user.id, 'email': user.email, 'username': user.username}
                if user_info not in current_user:
                    user_list.append(user_info)
            if user_list or current_user:
                msg = dict(result=True, user=user_list, cur_user=current_user)
                yield self.return_json(msg)
                return
            else:
                msg = dict(result=False, msg="没有可选的有效用户")
                yield self.return_json(msg)
                return
        elif do == 'adduser':
            pid = int(self.get_argument('project_id', default=0))
            users_id = self.get_arguments('project_users')
            mails = self.get_arguments('mail')
            user = []
            if len(mails) != len(users_id):
                msg = dict(result=False, msg='请求参数错误')
                yield self.return_json(msg)
                return
            mail = dict()
            for i in range(len(users_id)):
                mail[int(users_id[i])] = True if mails[i].lower() == 'true' else False
            if users_id:
                users = yield self.user.get_users_info_by_ids(users_id)
                for row in users:
                    user.append(json.dumps({'uid': row.id, 'email': row.email,
                                            'username': row.username, 'mail': mail[row.id]}))
            result, msg = yield self.project.edit_project(pid=pid, user=json.dumps(user))
            if result:
                msg = dict(result=True, msg='/admin/setting/project')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'getparam':
            pid = int(self.get_argument('pid', default=0))
            setting, total = yield self.setting.get_settings_list(pid=pid, s_type='param', limit=None)
            if setting:
                params = []
                for param in json.loads(setting[0].value):
                    params.append(json.loads(param))
                msg = dict(result=True, msg=params)
            else:
                msg = dict(result=False, msg=[])
            yield self.return_json(msg)
            return
        elif do == 'addparam':
            pid = int(self.get_argument('project_id', default=0))
            s_type = self.get_arguments('type')
            name = self.get_arguments('name')
            value = self.get_arguments('value')
            params = []
            for i in range(len(s_type)):
                argv = dict(type=s_type[i])
                if name[i].strip() != '' and value[i].strip() != '':
                    argv['name'] = '%s' % name[i]
                    argv['value'] = value[i]
                    params.append(argv)
            if len(s_type) != len(params):
                msg = dict(result=False, msg='参数配置不正确, 请检查, 所有参数为必填项')
                yield self.return_json(msg)
                return
            temp = list(set(name))
            if len(temp) != len(name):
                msg = dict(result=False, msg='参数名不能重复, 请检查')
                yield self.return_json(msg)
                return
            msg = ''
            for param in params:
                flag = False
                if param['type'] == 'Function':
                    for func in config.customs_func:
                        if param['value'] == func['name']:
                            flag = True
                            break
                    if not flag:
                        msg += ',{}'.format(param['name'])
            if msg != '':
                msg = dict(result=False, msg='方法变量【{}】所选自定义方法不存在'.format(msg[1:]))
                yield self.return_json(msg)
                return
            msg = ''
            for param in params:
                if param['type'] == 'Data':
                    argv, do = yield self.option_func.parse_sql_argv(param['value'], pid=pid)
                    if argv:
                        try:
                            test = TestingModule(**argv)
                            if do == 'SELECT':
                                yield test.get_one_result()
                                argv = True
                            else:
                                raise Exception('目前只支持SELECT方法', do)
                        except Exception as e:
                            log.warning(e)
                            argv = False
                    if not argv:
                        msg += ',{}'.format(param['name'])
            if msg != '':
                msg = dict(result=False, msg='数据源变量【{}】配置格式不对或sql执行出错, 请检查'.format(msg[1:]))
                yield self.return_json(msg)
                return
            for i in range(len(params)):
                params[i] = json.dumps(params[i])
            setting, total = yield self.setting.get_settings_list(pid=pid, s_type='param', limit=None)
            if setting:
                result, msg = yield self.setting.edit_setting(sid=setting[0].id, name=setting[0].project_name,
                                                              value=json.dumps(params))
            else:
                result, msg = yield self.setting.add_setting(pid=pid, s_type='param',
                                                             name='param', value=json.dumps(params))
            if result:
                msg = dict(result=True, msg=msg)
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return

    # host配置
    @gen.coroutine
    def __setting_host(self, do=''):
        if do == 'add':
            pid = int(self.get_argument('project', default=0))
            ip = self.get_argument('ip', default='')
            host = self.get_argument('host', default='')
            if not self.common_func.check_string(ip, 'ip') or not self.common_func.check_string(host, 'host'):
                msg = dict(result=False, msg='IP或Host的格式不正确')
                yield self.return_json(msg)
                return
            if pid == 0:
                project = yield self.project.get_projects_by_user(user=self.current_user.email, status=1)
                if self.current_user.role != 2:
                    project, total = yield self.project.get_projects_list(limit=None, status=1)
                if not project:
                    msg = dict(result=False, msg='没有项目,请先添加项目')
                    yield self.return_json(msg)
                    return
                pid_list = []
                pid_list_disable = []
                for row in project:
                    pid_list.append(row.id)
                s_host, total = yield self.setting.get_settings_list(s_type='host', limit=None)
                if total != 0:
                    for row in s_host:
                        if row.value == ip and row.name == host:
                            pid_list.remove(row.project_id)
                        elif row.name == host and row.value != ip:
                            pid_list_disable.append(row.project_id)
            else:
                s_host, total = yield self.setting.get_settings_list(pid=pid, s_type='host', name=host, limit=None)
                pid_list_disable = []
                for i in s_host:
                    if i.value == ip:
                        msg = dict(result=True, msg='/admin/setting/host')
                        yield self.return_json(msg)
                        return
                    else:
                        pid_list_disable.append(pid)
                pid_list = [pid]
            for pid in pid_list:
                if pid in pid_list_disable:
                    result, msg = yield self.setting.add_setting(pid, 'host', host, ip, 0)
                else:
                    result, msg = yield self.setting.add_setting(pid, 'host', host, ip)
                if not result:
                    msg = dict(result=False, msg=msg)
                    yield self.return_json(msg)
                    return
            msg = dict(result=True, msg='/admin/setting/host')
            yield self.return_json(msg)
            return
        elif do == 'delete':
            sid = int(self.get_argument('id', default=0))
            try:
                result, msg = yield self.setting.delete_setting(sid=sid)
            except Exception as e:
                log.error(e)
                result = False
                msg = e
            if result:
                msg = dict(result=True, msg='/admin/setting/host')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'update':
            pid = int(self.get_argument('pid', default=0))
            sid = int(self.get_argument('sid', default=0))
            status = self.get_argument('status', default='')
            host = self.get_argument('host', default='')
            if int(status) == 1:
                settings, total = yield self.setting.get_settings_list(pid=pid, s_type='host', name=host, limit=None)
                if len(settings) > 1:
                    for s in settings:
                        yield self.setting.edit_setting(sid=s.id, status=0)
                result, msg = yield self.setting.edit_setting(sid=int(sid), status=status)
            else:
                result, msg = yield self.setting.edit_setting(sid=int(sid), status=status)
            if result:
                msg = dict(result=True, msg='/admin/setting/host')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return

    # 接口配置
    @gen.coroutine
    def __setting_interface(self, do=''):
        if do == 'add':
            pid = int(self.get_argument('project', default=0))
            url = self.get_argument('url', default='')
            label = self.get_argument('label', default='')
            if pid == 0:
                msg = dict(result=False, msg='请先选择项目')
                yield self.return_json(msg)
                return
            if not self.common_func.check_string(url, 'url'):
                msg = dict(result=False, msg='接口地址格式不正确')
                yield self.return_json(msg)
                return
            interface, total = yield self.setting.get_settings_list(s_type='url', limit=None)
            if total != 0:
                for row in interface:
                    if json.loads(row.value)['url'] == url:
                        msg = dict(result=False, msg='在项目【{}】中已经存在该接口, 不同项目不能添加相同的接口'.format(row.project_name))
                        yield self.return_json(msg)
                        return
            urls = self.common_func.url_split(url)
            url = dict(url=url, label=label, key='', request_headers='', request_body='')
            result, msg = yield self.setting.add_setting(pid, 'url', '{}://{}'.format(urls['scheme'], urls['netloc']),
                                                         json.dumps(url, ensure_ascii=False))
            if result:
                msg = dict(result=True, msg='/admin/setting/interface')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'edit':
            sid = int(self.get_argument('sid', default=0))
            detail = self.get_argument('detail', default='')
            url = yield self.setting.get_setting_by_id(sid=sid)
            if url and url.type == 'url':
                value = json.loads(url.value)
                value['label'] = detail
                flag, msg = yield self.setting.edit_setting(sid=sid, value=json.dumps(value, ensure_ascii=False))
                if flag:
                    msg = dict(result=True, msg=msg)
                else:
                    msg = dict(result=False, msg=msg)
            else:
                msg = dict(result=False, msg='需要编辑的接口不存在')
            yield self.return_json(msg=msg)
            return
        elif do == 'delete':
            sid = int(self.get_argument('id', default=0))
            try:
                result, msg = yield self.setting.delete_setting(int(sid))
            except Exception as e:
                log.error(e)
                result = False
                msg = e
            if result:
                msg = dict(result=True, msg='/admin/setting/interface')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'params':
            sid = int(self.get_argument('sid', default=0))
            keys = self.get_argument('keys', default='')
            request_headers = self.get_argument('request_headers', default='')
            request_body = self.get_argument('request_body', default='')
            for key in keys.splitlines():
                if not self.common_func.check_string(string=key, str_type='check_key'):
                    msg = dict(result=False, msg='配置行 {} 格式不正确, 请检查'.format(key if len(key) <= 70 else key[:70]))
                    yield self.return_json(msg)
                    return
            setting = yield self.setting.get_setting_by_id(sid)
            if setting is None:
                msg = dict(result=False, msg='请求配置项不存在')
            else:
                setting = json.loads(setting.value)
                setting['key'] = keys
                setting['request_headers'] = escape.xhtml_escape(request_headers)
                setting['request_body'] = escape.xhtml_escape(request_body)
                result, msg = yield self.setting.edit_setting(sid=sid, value=json.dumps(setting, ensure_ascii=False))
                if result:
                    msg = dict(result=True, msg=msg)
                else:
                    msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'getparams':
            sid = int(self.get_argument('sid', default=0))
            setting = yield self.setting.get_setting_by_id(sid)
            if setting is None:
                msg = dict(result=False, msg='请求配置项不存在')
            else:
                setting = json.loads(setting.value)
                setting['request_body'] = escape.xhtml_unescape(setting['request_body'])
                setting['request_headers'] = escape.xhtml_unescape(setting['request_headers'])
                msg = dict(result=True, msg=setting)
            yield self.return_json(msg)
            return

    # 加解密配置
    @gen.coroutine
    def __setting_crypt(self, do=''):
        if do == 'add':
            pid = int(self.get_argument('project', default=0))
            encrypt = self.get_argument('encrypt', default='')
            encrypt_key = self.get_argument('encrypt-key', default='')
            encrypt_iv = self.get_argument('encrypt-iv', default='')
            decrypt = self.get_argument('decrypt', default='')
            decrypt_key = self.get_argument('decrypt-key', default='')
            decrypt_iv = self.get_argument('decrypt-iv', default='')
            if pid == 0:
                msg = dict(result=False, msg='请先选择项目')
                yield self.return_json(msg)
                return
            elif encrypt == '0':
                msg = dict(result=False, msg='请先选择加密方式')
                yield self.return_json(msg)
                return
            elif decrypt == '0':
                msg = dict(result=False, msg='请先选择解密方式')
                yield self.return_json(msg)
                return
            elif encrypt_key == '':
                msg = dict(result=False, msg='加密密钥不能为空')
                yield self.return_json(msg)
                return
            elif decrypt_key == '':
                msg = dict(result=False, msg='解密密钥不能为空')
                yield self.return_json(msg)
                return
            value = {'encrypt': {'name': encrypt, 'key': encrypt_key, 'iv': encrypt_iv},
                     'decrypt': {'name': decrypt, 'key': decrypt_key, 'iv': decrypt_iv}}
            pid_crypt, total = yield self.setting.get_settings_list(s_type='crypt', limit=None)
            if total != 0:
                for row in pid_crypt:
                    if row.project_id == pid:
                        result, msg = yield self.setting.edit_setting(
                            sid=row.id, value=json.dumps(value, ensure_ascii=False))
                        if result:
                            msg = dict(result=True, msg='/admin/setting/crypt')
                        else:
                            msg = dict(result=False, msg=msg)
                        yield self.return_json(msg)
                        return
            result, msg = yield self.setting.add_setting(
                pid, 'crypt', '{}+{}'.format(encrypt, decrypt), json.dumps(value, ensure_ascii=False))
            if result:
                msg = dict(result=True, msg='/admin/setting/crypt')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        elif do == 'delete':
            sid = int(self.get_argument('id', default=0))
            try:
                result, msg = yield self.setting.delete_setting(int(sid))
            except Exception as e:
                log.error(e)
                result = False
                msg = e
            if result:
                msg = dict(result=True, msg='/admin/setting/crypt')
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
