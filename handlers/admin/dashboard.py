from handlers.common import BaseHandler, authenticated_async
from tornado import gen


class DashboardHandler(BaseHandler):
    @authenticated_async
    @gen.coroutine
    def get(self):
        self.redirect('/admin/interface-test')
