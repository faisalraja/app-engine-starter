from lib.basehandler import BaseHandler

__author__ = 'faisal'


class Error404Handler(BaseHandler):
    def get(self):
        params = {'code': 404, 'title': 'Page Not Found', 'exception': self.request.route_args['exception']}
        self.response.set_status(params['code'])
        return self.render_template('errors/error.html', **params)


class Error403Handler(BaseHandler):
    def get(self):
        params = {'code': 403, 'title': 'Access Denied', 'exception': self.request.route_args['exception']}
        self.response.set_status(params['code'])
        return self.render_template('errors/error.html', **params)


class Error500Handler(BaseHandler):
    def get(self):
        params = {'code': 500, 'title': 'Server Error', 'exception': self.request.route_args['exception']}
        self.response.set_status(params['code'])
        return self.render_template('errors/error.html', **params)


class Error503Handler(BaseHandler):

    def setup_headers(self):
        self.response.set_status(429, 'Too Many Requests')
        self.response.headers.add_header('HTTP/1.1', '429 Too Many Requests')
        self.response.headers.add_header('Status', '429')
        self.response.headers.add_header('Retry-After', '3600')

    def get(self):
        params = {'code': 429, 'title': 'Too Many Request', 'exception': self.request.route_args['exception']}
        self.setup_headers()
        # todo you can implement re-captcha test here

        return self.render_template('errors/error.html', **params)