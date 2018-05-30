from handlers.common import BaseHandler, authenticated_async
from tornado import gen


class PluginHandler(BaseHandler):
    @authenticated_async
    @gen.coroutine
    def get(self, op='testdata'):
        if op == 'testdata':
            pass
        elif op == 'testcase':
            pass
        argv = dict(title='辅助工具', op=op)
        argv = dict(self.argv, **argv)
        self.render('admin/plugin.html', **argv)
