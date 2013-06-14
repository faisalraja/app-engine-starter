import logging
from lib.basehandler import BaseHandler, domain_user_required


class HomeHandler(BaseHandler):

    @domain_user_required
    def get(self):

        params = {}
        return self.render_template('admin/index.html', **params)