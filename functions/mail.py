from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from tornado_smtp.client import TornadoSMTP
from tornado import gen
from tornado.log import app_log as log
from munch import munchify
from functions.options import OptionsFunction
from modules.setting import SettingModule
from modules.project import ProjectModule
import json


class Mail(object):
    def __init__(self, smtp_server='', smtp_port='', use_ssl='',
                 smtp_user='', smtp_password='', mail_from=''):
        self.smtp_server = smtp_server if smtp_server != '' else 'localhost'
        self.smtp_port = smtp_port if smtp_port != '' else 25
        self.use_ssl = True if use_ssl == 'on' else False
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.mail_from = mail_from if mail_from != '' else smtp_user

    @gen.coroutine
    def _smtp_client(self):
        try:
            smtp = TornadoSMTP(host=self.smtp_server, port=self.smtp_port, use_ssl=self.use_ssl)
            yield smtp.login(user=self.smtp_user, password=self.smtp_password)
            return smtp, ''
        except Exception as e:
            log.warning(e)
            return None, e

    @gen.coroutine
    def send_mail(self, subject='[系统邮件]', message='', to=list()):
        smtp_client, res = yield self._smtp_client()
        if smtp_client is not None:
            msg = MIMEText(message, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['Sender'] = self.smtp_user
            msg['To'] = ', '.join(to)
            msg['From'] = formataddr(parseaddr('自动化测试系统邮件<{}>'.format(self.mail_from)))
            try:
                yield smtp_client.send_message(msg)
                yield smtp_client.quit()
                return True, ''
            except Exception as e:
                log.warning(e)
                yield smtp_client.quit()
                return False, e
        else:
            return False, res

    # 发送HTML格式报告邮件
    @gen.coroutine
    def send_html_report(self, rid):
        if rid:
            option_func = OptionsFunction()
            settings = SettingModule()
            lists = []
            pid = 0
            project = ''
            name = ''
            report_time = ''
            report_url = yield option_func.get_option_by_name('report_url')
            report_url = report_url if report_url else ''
            setting = yield settings.get_setting_by_id(rid)
            if setting and setting.type == 'report':
                report = json.loads(setting.value)
                pid = setting.project_id
                project = setting.project_name
                name = report['overview']['name']
                report_time = report['overview']['report_time']
                lists = report['report']
            for row in lists:
                if row['report']:
                    row['success_rate'] = '{:.2f} %'.format(row['success_test'] / row['total_test'] * 100)
                else:
                    row['success_rate'] = '0.00 %'
            lists = munchify(lists)
            for i in range(len(lists)):
                param = dict(id=i+1, suite_name=lists[i].suite_name, project=project, total_test=lists[i].total_test,
                             success_test=lists[i].success_test, fail_test=lists[i].fail_test, rid=rid,
                             success_rate=lists[i].success_rate, suite_id=lists[i].suite_id, report_url=report_url)
                if lists[i].result:
                    param['result'] = '<span class ="label label-info">通过</span>'
                else:
                    param['result'] = '<span class ="label label-danger">失败</span>'
                rows = """
                   <tr>
                       <td>{id}</td>
                       <td>{suite_name}</td>
                       <td>{project}</td>
                       <td>{total_test}</td>
                       <td>{success_test}</td>
                       <td>{fail_test}</td>
                       <td>{success_rate}</td>
                       <td>{result}</td>
                       <td><a class ="btn btn-primary" href="{report_url}/admin/interface-test/reports/list/{rid}/{suite_id}">查看详情</a></td>
                   </tr>""".format(**param)
                style = """
    <style type="text/css">
        .report-body * {
            -webkit-box-sizing: border-box;
            -moz-box-sizing: border-box;
            box-sizing: border-box;
        }
        .report-body {
            padding-top: 50px;
            padding-bottom: 40px;
            background-color: #eee;
            font-family: "Microsoft Yahei";
            font-size: 14px;
            line-height: 1.42857143;
            color: #333;
        }
        .report-body .container-fluid {
            margin-right: auto;
            margin-left: auto;
        }
        .report-body .well {
            min-height: 20px;
            padding: 19px;
            margin-bottom: 20px;
            background-color: #f5f5f5;
            border: 1px solid #e3e3e3;
            border-radius: 4px;
            box-shadow: inset 0 1px 1px rgba(0,0,0,.05);
        }
        .report-body .table-responsive {
            min-height: .01%;
            overflow-x: auto;
        }
        .report-body table {
            background-color: transparent;
            border-spacing: 0;
            border-collapse: collapse;
            border-color: grey;
        }
        .report-body thead {
            display: table-header-group;
            vertical-align: middle;
            vertical-align: middle;
        }
        .report-body tr {
            display: table-row;
            vertical-align: inherit;
            border-color: inherit;
        }
        .report-body th {
            text-align: left;
            font-weight: bold;
            display: table-cell;
        }
        .report-body tbody {
            display: table-row-group;
            vertical-align: middle;
            border-color: inherit;
        }
        .report-body .table {
            width: 100%;
            max-width: 100%;
            margin-bottom: 20px;
        }
        .report-body .table>thead:first-child>tr:first-child>th {
            border-top: 0;
        }
        .report-body .table>thead>tr>th {
            vertical-align: bottom;
            border-bottom: 2px solid #ddd;
            padding: 8px;
            line-height: 1.42857143;
        }
        .report-body .table>tbody>tr>td {
            padding: 8px;
            line-height: 1.42857143;
            vertical-align: top;
            border-top: 1px solid #ddd;
            display: table-cell;
        }
        .report-body .table-striped>tbody>tr:nth-of-type(odd) {
            background-color: #f9f9f9;
        }
        .report-body .label-info {
            background-color: #5bc0de;
        }
        .report-body .label-danger {
            background-color: #d9534f;
        }
        .report-body .label {
            display: inline;
            padding: .2em .6em .3em;
            font-size: 75%;
            font-weight: 700;
            line-height: 1;
            color: #fff;
            text-align: center;
            white-space: nowrap;
            vertical-align: baseline;
            border-radius: .25em;
        }
        .report-body .btn-primary {
            color: #fff;
            background-color: #337ab7;
            border-color: #2e6da4;
        }
        .report-body .btn {
            display: inline-block;
            padding: 6px 12px;
            margin-bottom: 0;
            font-size: 14px;
            font-weight: 400;
            line-height: 1.42857143;
            text-align: center;
            white-space: nowrap;
            vertical-align: middle;
            -ms-touch-action: manipulation;
            touch-action: manipulation;
            cursor: pointer;
            -webkit-user-select: none;
            -moz-user-select: none;
            -ms-user-select: none;
            user-select: none;
            background-image: none;
            border: 1px solid transparent;
            border-radius: 4px;
        }
        .report-body a {
            color: #337ab7;
            text-decoration: none;
        }
    </style>
"""
                content = """
<div class="report-body">
    <div class="container-fluid well">
        <h2 style="text-align: center;">任务 {name} 测试报告 / 报告时间 {report_time}</h2>
        <div class="table-responsive">
            <table class="table table-striped table-hover">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>用例名称</th>
                        <th>所属项目</th>
                        <th>测试接口数</th>
                        <th>通过数</th>
                        <th>失败数</th>
                        <th>通过率</th>
                        <th>测试结果</th>
                        <th>操作</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </div>
    {style}
</div>""".format(**dict(style=style, name=name, report_time=report_time, rows=rows))
                smtp_server = yield option_func.get_option_by_name('smtp_host')
                smtp_port = yield option_func.get_option_by_name('smtp_port')
                use_ssl = yield option_func.get_option_by_name('use_ssl')
                smtp_user = yield option_func.get_option_by_name('smtp_user')
                smtp_password = yield option_func.get_option_by_name('smtp_password')
                mail_from = yield option_func.get_option_by_name('mail_from')
                mail_report = yield option_func.get_option_by_name('mail_report')
                company = yield option_func.get_option_by_name('company')
                self.smtp_server = smtp_server if smtp_server else self.smtp_server
                self.smtp_port = smtp_port if smtp_port else self.smtp_port
                self.use_ssl = True if use_ssl == 'on' else self.use_ssl
                self.smtp_user = smtp_user if smtp_user else self.smtp_user
                self.smtp_password = smtp_password if smtp_password else self.smtp_password
                self.mail_from = mail_from if mail_from else self.mail_from
                mail_report = True if mail_report == 'on' else False
                users = yield ProjectModule().get_project(pid=pid, status=1)
                if users:
                    mail_to = []
                    users = json.loads(users.user) if users.user else []
                    for user in users:
                        user = json.loads(user)
                        if user['mail']:
                            mail_to.append(user['email'])
                    if mail_to and mail_report:
                        result, msg = yield self.send_mail(subject='[{}][测试报告]'.format(company),
                                                           message=content, to=mail_to)
                        if result:
                            log.info('发送任务 {} 测试报告邮件成功'.format(name))
                        else:
                            log.warning('发送任务 {} 测试报告邮件失败# {}'.format(name, msg))
