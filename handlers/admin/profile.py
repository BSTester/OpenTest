from tornado import gen
from handlers.common import BaseHandler, authenticated_async


# 个人信息操作类
class ProfileHandler(BaseHandler):
    @authenticated_async
    @gen.coroutine
    def get(self, op='info'):
        if op not in ['info', 'password']:
            self.redirect('/admin/profile')
            return
        argv = dict(title='个人信息', op=op)
        argv = dict(self.argv, **argv)
        self.render('admin/profile.html', **argv)

    @authenticated_async
    @gen.coroutine
    def post(self, op='info'):
        if op == 'info':
            email = self.get_argument('email', default='')
            username = self.get_argument('username', default='')
            realname = self.get_argument('realname', default='')
            if email == '' or not self.common_func.check_string(email, 'email'):
                msg = dict(result=False, msg='Email格式不正确')
            elif username == '' or not self.common_func.check_string(username, 'username'):
                msg = dict(result=False, msg='用户名格式不正确')
            elif realname != '' and not self.common_func.check_string(realname, 'realname'):
                msg = dict(result=False, msg='昵称格式不正确')
            else:
                user = yield self.user.get_user_info(email)
                if user is None:
                    msg = dict(result=False, msg='所编辑用户不存在')
                    yield self.return_json(msg)
                    return
                result, msg = yield self.user.edit_user(email, username=username, realname=realname)
                if result:
                    msg = dict(result=True, msg='个人信息修改成功')
                else:
                    msg = dict(result=False, msg='用户名 {} 已经被占用, 请更换用户名'.format(username))
            yield self.return_json(msg)
            return
        elif op == 'password':
            email = self.get_argument('email', default='')
            old_password = self.get_argument('old-password', default='')
            new_password = self.get_argument('new-password', default='')
            confirm_password = self.get_argument('confirm-password', default='')
            user = yield self.user.get_user_info(email)
            if user is None:
                msg = dict(result=False, msg='所编辑用户不存在')
                yield self.return_json(msg)
                return
            if email == '' or not self.common_func.check_string(email, 'email'):
                msg = dict(result=False, msg='Email格式不正确')
            elif self.common_func.encode_password(old_password) != user.password:
                msg = dict(result=False, msg='原密码不正确')
            elif self.common_func.encode_password(new_password) == user.password:
                msg = dict(result=False, msg='新密码不能与旧密码一样')
            elif new_password == '' or not self.common_func.check_string(new_password, 'password'):
                msg = dict(result=False, msg='新密码格式不正确')
            elif confirm_password != new_password:
                msg = dict(result=False, msg='确认密码与新密码输入不一致')
            else:
                result, msg = yield self.user.edit_user(email, password=new_password)
                if result:
                    msg = dict(result=True, msg='密码修改成功')
                else:
                    msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
            return
        else:
            self.redirect('/admin/profile/info')
