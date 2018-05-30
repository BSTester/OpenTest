from handlers.common import BaseHandler, authenticated_async
from tornado import gen, httpclient
from tornado.web import escape
from tornado.netutil import Resolver
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
from tornado.log import app_log as log
from phantomas import Phantomas
from functions.common import CommonFunction
import platform
import time
import os
import re
import json
import math
from munch import munchify
from handlers.admin.api import AddLogs


class PageHandler(BaseHandler):
    executor = ThreadPoolExecutor(100)
    Resolver.configure('tornado.netutil.ThreadedResolver')

    @authenticated_async
    @gen.coroutine
    def get(self, op='reports', page=1, limit=10):
        if not isinstance(limit, int):
            limit = int(limit)
        else:
            limit = limit if self.limit == '' else int(self.limit)
        try:
            page = int(page)
        except Exception as e:
            log.warning(e)
            page = 1
        page = 1 if int(page) <= 0 else int(page)
        lists = []
        total_page = 1
        if op == 'reports':
            res, total = yield self.setting.get_settings_list(s_type='page_report')
            total_page = int(math.ceil(total / limit))
            for row in res:
                report = json.loads(row.value)
                report['sid'] = row.id
                lists.append(munchify(report))
        elif op not in ['checklinks', 'checkpages']:
            self.redirect('/admin/page-test')
            return
        hosts = ''
        if platform.system().lower() == 'Windows'.lower():
            host_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
        else:
            host_path = '/etc/hosts'
        if os.path.exists(host_path):
            with open(host_path, 'r', encoding='utf8') as fp:
                hosts = fp.read()
                log.info('读取Hosts {} 配置成功'.format(host_path))
        argv = dict(title='页面监控', op=op, lists=lists, hosts=hosts, total_page=total_page, page=page, limit=limit)
        argv = dict(self.argv, **argv)
        self.render('admin/page.html', **argv)

    @authenticated_async
    @gen.coroutine
    def post(self, op='checklinks', do=''):
        if op == 'checklinks':
            name = self.get_argument('name', default='')
            links = self.get_argument('url', default='')
            exclude_links = self.get_argument('exclude_url', default='')
            check_all = self.get_argument('check_all', default='off')
            device = self.get_argument('device', default='PC')
            cookie = self.get_argument('cookie', default='')
            check_all = True if check_all == 'on' else False
            hosts = self.get_argument('hosts', default='')
            viewport = '1920x1080'
            if device == 'iPhone':
                user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1'
                viewport = '1080x1920'
            elif device == 'Android':
                user_agent = 'Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Mobile Safari/537.36'
                viewport = '1080x1920'
            else:
                user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            check_links = []
            check_history = []
            url_history = []
            error_links = ''
            for link in links.splitlines():
                link = link.strip()
                if link == '':
                    continue
                if self.common_func.check_string(string=link, str_type='url'):
                    check_links.append(link)
                else:
                    error_links += '{}</br>'.format(link)
            for link in exclude_links.splitlines():
                link = link.strip()
                if link == '':
                    continue
                if self.common_func.check_string(string=link, str_type='url'):
                    check_history.append(link)
                    url_history.append(link)
                else:
                    error_links += '{}</br>'.format(link)
            if error_links != '':
                msg = dict(result=False, msg='链接 {} 格式不正确, 请检查'.format(error_links))
            elif check_links:
                if platform.system().lower() == 'Windows'.lower():
                    host_path = 'C:\\Windows\\System32\\drivers\\etc\\hosts'
                else:
                    host_path = '/etc/hosts'
                if os.path.exists(host_path):
                    with open(host_path, 'w', encoding='utf8') as fp:
                        fp.write(hosts)
                        log.info('写入Hosts {} 配置 {} 成功'.format(host_path, hosts))
                result = yield self.__check_links(
                    name=name, check_links=check_links, check_history=check_history, url_history=url_history,
                    user_agent=user_agent, cookie=cookie, viewport=viewport, check_all=check_all)
                msg = dict(result=True, msg='/{}'.format(result))
                add_logs = AddLogs(tool_code='tool_checklinks', operate_ip=self.request.remote_ip)
                add_logs.add_logs()
            else:
                msg = dict(result=False, msg='入口链接不能为空')
            yield self.return_json(msg)
        elif op == 'reports' and do == 'delete':
            sid = int(self.get_argument('id', default=0))
            flag, msg = yield self.setting.delete_setting(sid=sid)
            if flag:
                msg = dict(result=True, msg=msg)
            else:
                msg = dict(result=False, msg=msg)
            yield self.return_json(msg=msg)
            return

    # 链接检查
    @gen.coroutine
    def __check_links(self, name, check_links, check_history=list(), url_history=list(), user_agent='', cookie='', viewport='1920x1080', check_all=False):
        log.info('页面链接检查开始')
        start_time = time.time()
        html_dir = 'static/results/html/{}'.format(time.strftime('%Y%m%d'))
        if not os.path.exists(html_dir):
            os.makedirs(html_dir)
        html_index = '{}/index.{}.html'.format(html_dir, time.time())
        text = ''
        for url in check_links:
            if url in url_history:
                log.info('链接 {} 已检查过或已排除'.format(url))
                continue
            next_links = []
            results = []
            code = 599
            reason = 'Unknown'
            title = ''
            try:
                links, next_links, resp = yield self.__get_links(
                    url=url, user_agent=user_agent, cookie=cookie, check_all=check_all)
                code = resp.code if resp else code
                reason = resp.reason if resp else reason
                body = resp.body if not isinstance(resp.body, bytes) else resp.body.decode('utf8', errors='ignore')
                title = re.findall(r'<title>(.*?)</title>', body if isinstance(body, str) else str(body))
                title = title[0] if title else ''
                for link in links:
                    if link['href'] in check_history:
                        log.info('链接 {} 已检查过或已排除'.format(link['href']))
                        continue
                    res = yield self.__hot_link_check(url=link['href'], user_agent=user_agent, cookie=cookie)
                    res['text'] = link['text']
                    results.append(res)
                    check_history.append(link['href'])
                load_results = yield self.__phantomas_check(url=url, user_agent=user_agent, cookie=cookie, viewport=viewport)
            except Exception as e:
                log.error('链接 {} 检查出现异常#{}'.format(url, e))
                load_results = dict(url=url, screenshot='', har='', results=dict())
            url_history.append(url)
            for link in next_links:
                if link not in check_links:
                    check_links.append(link)
            html_file = yield self.__gen_report(results_dir=html_dir, results=results, load_results=load_results)
            log.info('生成链接 {} 扫描报告 /{}'.format(url, html_file))
            text += '<li><b>[{} {}]</b> {} >> <a href="/{}" target="_blank">{}</a></li>'.format(
                code, reason, title, html_file, url)
        html = """
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
	<title>页面链接扫描报告</title>
    <style type="text/css">
		h2, p {text-align: center;}
		li {padding-bottom: 5px;}
	</style>
</head>
<body>
	<div>
		<h2>页面链接扫描报告</h2>
		<div>
			<ul>
			    %s
			</ul>
		</div>
	</div>
</body>
</html>
""" % text
        with open(html_index, 'w') as fp:
            fp.write(html)
        log.info('生成页面链接扫描报告 /{}'.format(html_index))
        log.info('页面链接检查结束')
        report_time = time.time()
        elapsed_time = report_time - start_time
        name = name.strip() if name.strip() != '' else '页面链接检查_{}'.format(time.strftime('%Y%m%d%H%M%S'))
        reports = dict(
            name=name, total_links=len(check_links), elapsed_time=elapsed_time, report_url='/{}'.format(html_index),
            start_time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(start_time) + 3600 * 8)),
            report_time=time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(report_time) + 3600 * 8)))
        pid = yield self.project.get_project(name='页面链接检查')
        if not pid:
            pid, msg = yield self.project.add_project(name='页面链接检查')
        else:
            pid = pid.id
        self.setting.add_setting(pid=pid, s_type='page_report', name=name,
                                 value=json.dumps(reports, ensure_ascii=False))
        return html_index

    # 请求操作
    @gen.coroutine
    def __request_url(self, url, user_agent='', cookie=''):
        page_client = httpclient.AsyncHTTPClient(max_clients=100)
        headers = {'User-Agent': user_agent, 'Cookie': cookie}
        argv = dict(method='GET', headers=headers, request_timeout=120, validate_cert=False, raise_error=False)
        try:
            response = yield page_client.fetch(url, **argv)
        except httpclient.HTTPError as e:
            log.warning('请求页面 {} 异常, 异常信息 {}'.format(url, str(e.response.error if e.response else e)))
            response = None
        # page_client.close()
        if response and response.code in [301, 302]:
            for cookies in response.headers.get_list('Set-Cookie'):
                cookie += '{};'.format(cookies)
            url = response.headers.get('Location')
            response = yield self.__request_url(url=url, user_agent=user_agent, cookie=cookie)
        return response

    # 获取页面链接
    @gen.coroutine
    def __get_links(self, url, user_agent='', cookie='', check_all=False):
        response = yield self.__request_url(url, user_agent, cookie)
        common_func = CommonFunction()
        url_split = common_func.url_split(url)
        host = url_split.host
        scheme = url_split.scheme
        netloc = '{}://{}'.format(scheme, url_split.netloc)
        links = []
        if response and response.body:
            body = response.body if not isinstance(response.body, bytes) else response.body.decode('utf8', errors='ignore')
            body = body if isinstance(body, str) else str(body)
            link_a = re.findall(r'<a.*?href=[\'"](.*?)[\'"].*?title=[\'"](.*?)[\'"].*?>(.*?)</a>', body)
            link_b = re.findall(r'<a.*?title=[\'"](.*?)[\'"].*?href=[\'"](.*?)[\'"].*?>(.*?)</a>', body)
            link_c = re.findall(r'<a.*?href=[\'"](.*?)[\'"].*?>(.*?)</a>', body)
            link_d = re.findall(r'data-href=[\'"](.*?)[\'"]', body)
            link_e = re.findall(r'data-url=[\'"](.*?)[\'"]', body)
            for link in link_a:
                href = link[0].strip()
                if re.match(r'^(http|https):', href) is not None:
                    pass
                elif re.match(r'^//', href) is not None:
                    href = scheme + href
                elif re.match(r'^/', href) is not None:
                    href = netloc + href
                elif re.match(r'^(javascript|#)', href.lower()) is not None:
                    continue
                else:
                    href = '{}/{}'.format(url, href)
                title = link[1]
                text = link[2] if link[2] != '' else link[1]
                log.info('获取到链接: {} {}'.format(text, href))
                link = dict(href=href, title=title, text=text)
                if link not in links:
                    links.append(link)
            for link in link_b:
                href = link[1].strip()
                if re.match(r'^(http|https):', href) is not None:
                    pass
                elif re.match(r'^//', href) is not None:
                    href = scheme + href
                elif re.match(r'^/', href) is not None:
                    href = netloc + href
                elif re.match(r'^(javascript|#)', href.lower()) is not None:
                    continue
                else:
                    href = '{}/{}'.format(url, href)
                title = link[0]
                text = link[2] if link[2] != '' else link[0]
                log.info('获取到链接: {} {}'.format(text, href))
                link = dict(href=href, title=title, text=text)
                if link not in links:
                    links.append(link)
            for link in link_c:
                href = link[0].strip()
                if re.match(r'^(http|https):', href) is not None:
                    pass
                elif re.match(r'^//', href) is not None:
                    href = scheme + href
                elif re.match(r'^/', href) is not None:
                    href = netloc + href
                elif re.match(r'^(javascript|#)', href.lower()) is not None:
                    continue
                else:
                    href = '{}/{}'.format(url, href)
                title = ''
                text = link[1]
                log.info('获取到链接: {} {}'.format(text, href))
                link = dict(href=href, title=title, text=text)
                if link not in links:
                    links.append(link)
            for link in link_d + link_e:
                href = link[0].strip()
                if re.match(r'^(http|https):', href) is not None:
                    pass
                elif re.match(r'^//', href) is not None:
                    href = scheme + href
                elif re.match(r'^/', href) is not None:
                    href = netloc + href
                elif re.match(r'^(javascript|#)', href.lower()) is not None:
                    continue
                else:
                    href = '{}/{}'.format(url, href)
                title = ''
                text = ''
                log.info('获取到链接: {} {}'.format(text, href))
                link = dict(href=href, title=title, text=text)
                if link not in links:
                    links.append(link)
        next_links = []
        if check_all:
            for link in links:
                cur_host = common_func.url_split(link['href']).host
                if cur_host == host and link['href'] not in next_links:
                    next_links.append(link['href'])
        return links, next_links, response

    # 跳转链接检查
    @gen.coroutine
    def __hot_link_check(self, url, user_agent='', cookie=''):
        results = dict(url='', code=599, reason='Unknown', title='')
        response = yield self.__request_url(url, user_agent, cookie)
        if response:
            body = response.body if not isinstance(response.body, bytes) else response.body.decode('utf8', errors='ignore')
            title = re.findall(r'<title>(.*?)</title>', body if isinstance(body, str) else str(body))
            title = title[0] if title else ''
            results = dict(url=url, code=response.code, reason=response.reason, title=title)
            log.info('检查链接: {} {} {} {}'.format(response.code, response.reason, title, url))
        return results

    # Phantomas页面动态链接检查
    @run_on_executor
    def __phantomas_check(self, url, user_agent='', cookie='', runs=1, viewport='1920x1080'):
        if platform.system().lower() == 'Windows'.lower():
            exec_path = 'phantomas.cmd'
        else:
            exec_path = 'phantomas'
        screenshot_dir = 'static/results/screenshot'
        har_dir = 'static/results/har'
        if not os.path.exists(screenshot_dir):
            os.mkdir(screenshot_dir)
        if not os.path.exists(har_dir):
            os.mkdir(har_dir)
        screenshot_file = '{}/{}.png'.format(screenshot_dir, time.time())
        har_file = '{}/{}.har'.format(har_dir, time.time())
        param = dict(url=url, exec_path=exec_path, timeout=120, scroll=True, viewport=viewport,
                     screenshot=screenshot_file, har=har_file, ignore_ssl_errors=True, runs=runs,
                     user_agent=user_agent, cookie=cookie)
        try:
            results = Phantomas(**param).run()
        except Exception as e:
            log.error('{} 加载失败#{}'.format(url, e))
            results = None
        check_results = dict(ajaxRequests='', cssCount='', jsCount='', jsonCount='', imageCount='', webfontCount='',
                             videoCount='', iframesCount='', otherCount='', domains='', notFound='')
        if results:
            ajaxRequests = results.get_offenders('ajaxRequests') if runs == 1 else results.runs[0].get_offenders('ajaxRequests')
            cssCount = results.get_offenders('cssCount') if runs == 1 else results.runs[0].get_offenders('cssCount')
            jsCount = results.get_offenders('jsCount') if runs == 1 else results.runs[0].get_offenders('jsCount')
            jsonCount = results.get_offenders('jsonCount') if runs == 1 else results.runs[0].get_offenders('jsonCount')
            imageCount = results.get_offenders('imageCount') if runs == 1 else results.runs[0].get_offenders('imageCount')
            webfontCount = results.get_offenders('webfontCount') if runs == 1 else results.runs[0].get_offenders('webfontCount')
            videoCount = results.get_offenders('videoCount') if runs == 1 else results.runs[0].get_offenders('videoCount')
            iframesCount = results.get_offenders('iframesCount') if runs == 1 else results.runs[0].get_offenders('iframesCount')
            otherCount = results.get_offenders('otherCount') if runs == 1 else results.runs[0].get_offenders('otherCount')
            domains = results.get_offenders('domains') if runs == 1 else results.runs[0].get_offenders('domains')
            notFound = results.get_offenders('notFound') if runs == 1 else results.runs[0].get_offenders('notFound')
            log.info('ajaxRequests: {}'.format(ajaxRequests))
            log.info('cssCount: {}'.format(cssCount))
            log.info('jsCount: {}'.format(jsCount))
            log.info('jsonCount: {}'.format(jsonCount))
            log.info('imageCount: {}'.format(imageCount))
            log.info('webfontCount: {}'.format(webfontCount))
            log.info('videoCount: {}'.format(videoCount))
            log.info('iframesCount: {}'.format(iframesCount))
            log.info('otherCount: {}'.format(otherCount))
            log.info('domains: {}'.format(domains))
            log.info('notFound: {}'.format(notFound))
            check_results = dict(ajaxRequests=ajaxRequests, cssCount=cssCount, jsCount=jsCount, jsonCount=jsonCount,
                                 imageCount=imageCount, webfontCount=webfontCount, videoCount=videoCount,
                                 iframesCount=iframesCount, otherCount=otherCount, domains=domains, notFound=notFound)
        return dict(url=url, screenshot=screenshot_file, har=har_file, results=check_results)

    # 生成测试报告
    @run_on_executor
    def __gen_report(self, results_dir, results, load_results):
        html_file = '{}/{}.html'.format(results_dir, time.time())
        results = sorted(results, key=lambda r: r['code'], reverse=True)
        s = ''
        if 'notFound' in load_results['results'].keys() and load_results['results']['notFound']:
            s += '<li><h4>notFound ({})</h4><ul>'.format(len(load_results['results']['notFound']))
            for res in load_results['results']['notFound']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if results:
            s += '<li><h4>links ({})</h4><ul>'.format(len(results))
            for res in results:
                s += """
                    <li>|--- <b>[{} {}]</b> <b>Page Title:</b> {}, <b>Link Title:</b> {} >> {}</li>
""".format(res['code'], res['reason'], escape.xhtml_escape(res['title']), escape.xhtml_escape(res['text']), escape.xhtml_escape(res['url']))
            s += '</ul></li>'
        if 'cssCount' in load_results['results'].keys() and load_results['results']['cssCount']:
            s += '<li><h4>cssCount ({})</h4><ul>'.format(len(load_results['results']['cssCount']))
            for res in load_results['results']['cssCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'jsCount' in load_results['results'].keys() and load_results['results']['jsCount']:
            s += '<li><h4>jsCount ({})</h4><ul>'.format(len(load_results['results']['jsCount']))
            for res in load_results['results']['jsCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'imageCount' in load_results['results'].keys() and load_results['results']['imageCount']:
            s += '<li><h4>imageCount ({})</h4><ul>'.format(len(load_results['results']['imageCount']))
            for res in load_results['results']['imageCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'jsonCount' in load_results['results'].keys() and load_results['results']['jsonCount']:
            s += '<li><h4>jsonCount ({})</h4><ul>'.format(len(load_results['results']['jsonCount']))
            for res in load_results['results']['jsonCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'ajaxRequests' in load_results['results'].keys() and load_results['results']['ajaxRequests']:
            s += '<li><h4>ajaxRequests ({})</h4><ul>'.format(len(load_results['results']['ajaxRequests']))
            for res in load_results['results']['ajaxRequests']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'webfontCount' in load_results['results'].keys() and load_results['results']['webfontCount']:
            s += '<li><h4>webfontCount ({})</h4><ul>'.format(len(load_results['results']['webfontCount']))
            for res in load_results['results']['webfontCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'videoCount' in load_results['results'].keys() and load_results['results']['videoCount']:
            s += '<li><h4>videoCount ({})</h4><ul>'.format(len(load_results['results']['videoCount']))
            for res in load_results['results']['videoCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'iframesCount' in load_results['results'].keys() and load_results['results']['iframesCount']:
            s += '<li><h4>iframesCount ({})</h4><ul>'.format(len(load_results['results']['iframesCount']))
            for res in load_results['results']['iframesCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'otherCount' in load_results['results'].keys() and load_results['results']['otherCount']:
            s += '<li><h4>otherCount ({})</h4><ul>'.format(len(load_results['results']['otherCount']))
            for res in load_results['results']['otherCount']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        if 'domains' in load_results['results'].keys() and load_results['results']['domains']:
            s += '<li><h4>domains ({})</h4><ul>'.format(len(load_results['results']['domains']))
            for res in load_results['results']['domains']:
                s += """
                    <li>|--- {}</li>
""".format(escape.xhtml_escape(res))
            s += '</ul></li>'
        text = """
<!doctype html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
	<title>页面链接扫描报告 - %(url)s</title>
    <style type="text/css">
		h2, p {text-align: center;}
		li ul {list-style-type: none; margin-top: -20px;}
	</style>
</head>
<body>
	<div>
		<h2>页面链接扫描报告 - %(url)s</h2>
		<p><a href="/%(screenshot)s" target="_blank">查看页面截图</a><!--a href="/%(har)s" target="_blank">查看页面HTTP请求/响应信息(HTTP Archive)</a--></p>
		<div>
			<ul>
			    %(res)s
			</ul>
		</div>
	</div>
</body>
</html>
""" % (dict(url=load_results['url'], screenshot=load_results['screenshot'], har=load_results['har'], res=s))
        with open(html_file, 'w') as fp:
            fp.write(text)
        return html_file
