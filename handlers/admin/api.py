import time
from handlers.common import BaseHandler
from tornado import gen, httpclient, httputil


class AddLogs(object):
    def __init__(self, tool_code='tool_opentest', operate_ip='::1'):
        self.url = 'http://172.20.20.160:8080/xiaoniu_web_timp/tool_log_add'
        self.data = dict(tool_code=tool_code, operate_ip=operate_ip)

    @gen.coroutine
    def add_logs(self):
        api_client = httpclient.AsyncHTTPClient()
        yield api_client.fetch(self.url, method='POST', body=httputil.urlencode(self.data))
        # api_client.close()


# 登录操作类
class LoginHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        yield self.__login_or_register()

    @gen.coroutine
    def post(self):
        yield self.__login_or_register()

    @gen.coroutine
    def __login_or_register(self):
        self.clear_cookie('BSTSESSION')
        username = self.get_argument('username', default='').strip()
        email = self.get_argument('email', default='').strip()
        password = self.get_argument('password', default='123456').strip()
        if (username == '' and email == '') or password == '':
            self.redirect('/admin/register')
            return
        username = email if email != '' else username
        user = yield self.user.get_user_info(username)
        add_logs = AddLogs(operate_ip=self.request.remote_ip)
        if not user:
            if not self.common_func.check_string(username, 'email'):
                self.redirect('/admin/register')
            else:
                result, msg = yield self.user.register_user(username, password)
                if result:
                    self.set_secure_cookie('BSTSESSION', username, 1)
                    add_logs.add_logs()
                    self.redirect('/admin/profile')
                    return
                else:
                    self.redirect('/admin/register')
                    return
        if user.password == self.common_func.encode_password(password) and user.status == 1:
            self.user.edit_user(username, last_login_time=time.strftime('%Y-%m-%d %H:%M:%S'))
            self.set_secure_cookie('BSTSESSION', user.email, 1)
            add_logs.add_logs()
            self.redirect('/admin/dashboard')
        else:
            self.redirect('/admin/login')
