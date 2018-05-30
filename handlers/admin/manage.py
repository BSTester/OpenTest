from tornado import gen
from handlers.common import BaseHandler, authenticated_async
from functions.mail import Mail
from functions.common import CommonFunction
from munch import munchify
import math
import time


class ManageHandler(BaseHandler):
    """
    管理员后台相关配置
    """
    @authenticated_async
    @gen.coroutine
    def get(self, op='option', page=1, limit=10):
        if self.current_user.role == 2:
            self.redirect('/admin/dashboard')
            return
        argv = dict(title='管理后台', op=op)
        if not isinstance(limit, int):
            limit = int(limit)
        else:
            limit = limit if self.limit == '' else int(self.limit)
        page = 1 if int(page) <= 0 else int(page)
        if op == 'option':
            if self.current_user.role == 1:
                self.redirect('/admin/manage/users')
                return
            option = dict(company='', page_limit='', email_ext='', smtp_host='', mail_from='', mail_report='',
                          smtp_port='', smtp_user='', smtp_password='', use_ssl='', report_url='')
            options = yield self.option.get_options_list()
            for key in option:
                for op in options:
                    if key == op.name:
                        option[key] = op.value
                        break
            argv = dict(option=munchify(option), **argv)
        elif op == 'users':
            lists, total = yield self.user.get_users_list(page=page, limit=limit)
            total_page = int(math.ceil(total / limit))
            argv = dict(lists=lists, page=page, limit=limit, total_page=total_page, **argv)
            total_page = 1 if total_page <= 0 else total_page
            if total_page < page:
                self.redirect('/admin/manage/{}/{}/{}'.format(op, total_page, limit))
                return
        elif op == 'logs':
            lists, total = yield self.setting.get_settings_list(s_type='log', page=page, limit=limit)
            total_page = int(math.ceil(total / limit))
            for row in lists:
                row.name = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(float(row.name)))
            argv = dict(lists=lists, page=page, limit=limit, total=total, total_page=total_page, **argv)
            total_page = 1 if total_page <= 0 else total_page
            if total_page < page:
                self.redirect('/admin/manage/{}/{}/{}'.format(op, total_page, limit))
                return
        else:
            self.redirect('/admin/manage')
            return
        argv = dict(self.argv, **argv)
        self.render('admin/manage.html', **argv)

    @authenticated_async
    @gen.coroutine
    def post(self, op='option', do='save'):
        if self.current_user.role == 2:
            msg = dict(result=False, msg='请使用管理员登录后再进行操作!')
            yield self.return_json(msg)
            return
        if op == 'option':
            company = self.get_argument('company', default='')
            page_limit = self.get_argument('page_limit', default='')
            email_ext = self.get_argument('email_ext', default='')
            smtp_host = self.get_argument('smtp_host', default='')
            smtp_port = self.get_argument('smtp_port', default='')
            use_ssl = self.get_argument('use_ssl', default='off')
            smtp_user = self.get_argument('smtp_user', default='')
            smtp_password = self.get_argument('smtp_password', default='')
            mail_from = self.get_argument('mail_from', default='')
            report_url = self.get_argument('report_url', default='')
            mail_report = self.get_argument('mail_report', default='off')
            common_func = CommonFunction()
            if smtp_user != '' and not common_func.check_string(smtp_user, 'email'):
                msg = dict(result=False, msg='【SMTP 登录用户】必须是Email格式')
                yield self.return_json(msg)
                return
            if mail_from != '' and not common_func.check_string(mail_from, 'email'):
                msg = dict(result=False, msg='【发件人显示为】必须是Email格式')
                yield self.return_json(msg)
                return
            if do == 'test':
                send_to = self.get_argument('send_to', default='')
                if '' in (send_to, smtp_port, smtp_host, smtp_user, smtp_password):
                    msg = dict(result=False, msg='所有配置不能为空, 请检查配置是否正确')
                    yield self.return_json(msg)
                    return
                if not common_func.check_string(send_to, 'email'):
                    msg = dict(result=False, msg='【配置测试】地址必须是Email格式')
                    yield self.return_json(msg)
                    return
                mail = Mail(smtp_server=smtp_host, smtp_port=smtp_port, use_ssl=use_ssl,
                            smtp_user=smtp_user, smtp_password=smtp_password, mail_from=mail_from)
                message = '<p>[{}]邮件配置测试, 收到此邮件说明配置正确。</p>'.format(self.company)
                result, msg = yield mail.send_mail(subject='[{}][系统测试邮件]'.format(self.company),
                                                   message=message, to=[send_to])
                if result:
                    msg = dict(result=True, msg='邮件发送成功')
                else:
                    msg = dict(result=False, msg='邮件发送失败, {}'.format(msg))
            else:
                if page_limit == '':
                    page_limit = 0
                else:
                    page_limit = int(page_limit)
                if len(company) < 2 or len(company) > 60:
                    msg = dict(result=False, msg='【公司名称】格式不正确')
                    yield self.return_json(msg)
                    return
                if page_limit < 10 or page_limit > 100 or page_limit % 10 != 0:
                    msg = dict(result=False, msg='【分页数目】必须为10的倍数且是10与100之间的整数')
                    yield self.return_json(msg)
                    return
                if report_url != '' and not common_func.check_string(report_url, 'url'):
                    msg = dict(result=False, msg='【邮件报告链接域名】格式不对, 请检查')
                    yield self.return_json(msg)
                    return
                edit_options = dict(company=company, page_limit=page_limit, email_ext=email_ext, report_url=report_url,
                                    smtp_host=smtp_host, smtp_port=smtp_port, smtp_user=smtp_user, mail_report=mail_report,
                                    smtp_password=smtp_password, use_ssl=use_ssl, mail_from=mail_from)
                options = yield self.option.get_options_list()
                flag = True
                msg = ''
                options_name = []
                for option in options:
                    options_name.append(option.name)
                if options_name:
                    for option in edit_options:
                        if option in options_name:
                            result, msg = yield self.option.edit_option(name=option, value=edit_options[option])
                        else:
                            result, msg = yield self.option.add_option(name=option, value=edit_options[option])
                        if not result:
                            flag = False
                            break
                else:
                    for option in edit_options:
                        result, msg = yield self.option.add_option(name=option, value=edit_options[option])
                        if not result:
                            flag = False
                            break
                if flag:
                    msg = dict(result=True, msg='更新系统配置成功')
                else:
                    msg = dict(result=False, msg=msg)
            yield self.return_json(msg)
        elif op == 'users':
            if do == 'add':
                email = self.get_argument('email', default='')
                if self.common_func.check_string(email, 'email'):
                    user = yield self.user.get_user_info(email)
                    if user is None:
                        self.user.register_user(email, '123456')
                self.redirect('/admin/manage/users')
                return
            uid = self.get_argument('id', default='')
            user = yield self.user.get_users_info_by_ids(ids=[uid])
            if not user:
                msg = dict(result=False, msg='所编辑的用户不存在')
                yield self.return_json(msg)
                return
            if do == 'status':
                status = int(self.get_argument('status', default=0))
                result, msg = yield self.user.edit_user(email=user[0].email, status=status)
                if result:
                    msg = dict(result=True, msg=msg)
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg)
                return
            elif do == 'role':
                role = int(self.get_argument('role', default=0))
                result, msg = yield self.user.edit_user(email=user[0].email, role=role)
                if result:
                    msg = dict(result=True, msg=msg)
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg)
                return
            elif do == 'reset':
                result, msg = yield self.user.edit_user(email=user[0].email, password='123456')
                if result:
                    msg = dict(result=True, msg='用户 {} 的密码已重置为 123456'.format(user[0].email))
                else:
                    msg = dict(result=False, msg=msg)
                yield self.return_json(msg)
                return
        elif op == 'logs':
            yield self.setting.delete_settings_list(s_type='log')
            self.redirect('/admin/manage/logs')
