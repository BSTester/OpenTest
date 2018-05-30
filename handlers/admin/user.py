from handlers.common import BaseHandler
from tornado import gen
from urllib.parse import unquote, urlsplit
from handlers.admin.api import AddLogs
import time


# 登录操作类
class LoginHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        if self.get_secure_cookie('BSTSESSION', None) is not None:
            self.redirect('/admin/dashboard')
        else:
            self.render('login.html', title='登录', company=self.company)

    @gen.coroutine
    def post(self):
        username = self.get_argument('username', default='')
        password = self.get_argument('password', default='')
        user = yield self.user.get_user_info(username)
        if not user:
            msg = dict(result=False, error='username', msg='用户名不正确!')
            yield self.return_json(msg)
            return
        if user.password == self.common_func.encode_password(password) and user.status == 1:
            self.user.edit_user(username, last_login_time=time.strftime('%Y-%m-%d %H:%M:%S'))
            self.set_secure_cookie('BSTSESSION', user.email, 1)
            url = '/admin/dashboard'
            query = self.request.headers['Referer']
            if query != '':
                query = unquote(urlsplit(query).query)
                query = query.split(sep='=', maxsplit=1)
                if len(query) == 2:
                    url = query[1]
            add_logs = AddLogs(operate_ip=self.request.remote_ip)
            add_logs.add_logs()
            self.redirect(url)
            return
        elif user.status == 0:
            msg = dict(result=False, error='username', msg='用户已被禁用, 请联系管理员!')
        else:
            msg = dict(result=False, error='password', msg='密码不正确!')
        yield self.return_json(msg)


# 注册操作类
class RegisterHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        email_ext = yield self.option.get_option(name='email_ext')
        email_ext = email_ext.value if email_ext else ''
        self.render('register.html', title='注册', company=self.company, email_ext=email_ext)

    @gen.coroutine
    def post(self, op=None):
        username = self.get_argument('username', default='')
        email_ext = yield self.option.get_option(name='email_ext')
        email_ext = email_ext.value if email_ext else ''
        if email_ext != '':
            username = '{}@{}'.format(username, email_ext)
        if op == 'check':
            user = yield self.user.get_user_info(username)
            if user is not None:
                msg = dict(result=False, msg='该用户已存在')
            elif username.count('@') > 1:
                msg = dict(result=False, msg='不能包含"@"')
            else:
                msg = dict(result=True, msg='用户不存在，可以注册')
            yield self.return_json(msg)
            return
        password = self.get_argument('password', default='')
        confirm_password = self.get_argument('confirm_password', default='')
        if not self.common_func.check_string(username, 'email'):
            result = False
        elif not self.common_func.check_string(password, 'password'):
            result = False
        elif password != confirm_password:
            result = False
        else:
            user = yield self.user.get_user_info(email_or_username=username)
            if user is not None:
                self.redirect('/admin/register')
                return
            result, msg = yield self.user.register_user(username, password)
        if result:
            self.set_secure_cookie('BSTSESSION', username, 1)
            add_logs = AddLogs(operate_ip=self.request.remote_ip)
            add_logs.add_logs()
            self.redirect('/admin/profile')
            return
        else:
            self.redirect('/admin/register')
            return


# 退出操作类
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie('BSTSESSION')
        self.redirect('/')
