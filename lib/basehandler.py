import json
import os
import base64
import logging
import hashlib
from google.appengine.api.modules import modules
import webapp2
import config
from datetime import datetime
from google.appengine.api import users, app_identity, memcache
from google.appengine.ext import ndb
from webapp2_extras import jinja2
from webapp2_extras import sessions
from lib import jsonrpc, utils

# Initialize constants & stuff for static files

VERSION_ID = os.environ.get('CURRENT_VERSION_ID', '1.1').split('.')
VERSION = VERSION_ID[0]
APP_VERSION = int(VERSION_ID[1])

IS_DEV = os.environ.get('SERVER_SOFTWARE', 'Development/%s' % VERSION_ID).startswith('Dev')

# Bot user agents
BOT_USER_AGENTS = [
    'Googlebot',
    'Yahoo! Slurp',
    'YahooSeeker',
    'bingbot',
    'iaskspider'
]


def user_required(handler):
    """
         Decorator for checking if there's a user associated
         with the current session.
         Will also fail if there's no session present.
    """

    def check_login(self, *args, **kwargs):
        """
            If handler has no login_url specified invoke a 403 error
        """
        if not self.user_id:
            try:
                self.redirect(self.uri_for('user-login'), abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_login


def domain_user_required(handler):
    """
         Decorator for checking if there's a admin/domain user associated
         with the current session.
         Will also fail if there's no session present.
    """

    def check_login(self, *args, **kwargs):
        # Check if admin
        user = users.get_current_user()
        if user is not None and user.nickname().find('@%s' % os.environ.get('HTTP_HOST')) != -1 or \
                users.is_current_user_admin():
            return handler(self, *args, **kwargs)
        elif user is not None:
            self.abort(403)
        else:
            try:
                self.redirect(self.uri_for('user-login'), abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)

    return check_login


class BaseHandler(webapp2.RequestHandler):
    """
        BaseHandler for all requests
    """

    def dispatch(self):
        """
        Here there are bunch of stuff happening
        The rate limiting allows you to not serve more request that might be an auto generated request
        The appspot restriction is if you want appspot.com to be password protected and serve to your main domain
        """

        # rate limiting check
        if config.rate_limit:
            self._rate_limiter()
        # appspot domain restriction check
        if config.restricted_auth and self._is_restricted():
            return self.response.write(self.jinja2.render_template('errors/restricted.html'))
        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    def _is_restricted(self):
        """
        restrict appspot domains or staging and duplicate contents
        """
        if filter(lambda p: p in self.request.path, ('/callback/', '/_ah/', '/task/')):
            # Useful for testing thirdparty callbacks
            pass
        elif self.request.host.endswith('.appspot.com') and \
                not self.request.headers.get('X-AppEngine-Cron') and \
                not self.request.headers.get('X-Appengine-Taskname'):

            if base64.decodestring(self.request.headers.get('Authorization', '')[6:]) != config.restricted_auth:
                self.response.headers['WWW-Authenticate'] = 'Basic realm=Restricted'
                self.response.set_status(401)
                return True
        return False

    def _rate_limiter(self):
        """
        Rate limiting for bots & save resources
        The reason we use 503 is because webapp2 does not have 429 code in it's
        supported codes because it's not official status code yet
        """
        user_agent = self.request.headers.get('User-Agent', 'Googlebot')
        robot = filter(lambda bot: user_agent.find(bot) != -1, BOT_USER_AGENTS)
        if robot:
            # use current minute cache
            ctx = ndb.get_context()
            cache_id = 'rate_limiter_{}'.format(hashlib.md5(robot.pop()).hexdigest())
            request_count = ctx.memcache_incr(cache_id, initial_value=0).get_result()
            if request_count >= config.rate_limit[0]:
                self.abort(503)
            elif request_count == 1:
                ctx.memcache_set(cache_id, request_count, config.rate_limit[1])
        else:
            # rate limiters for non bots non logged users
            request_count, time_started = self.session.get('rate_limiter_request', (0, datetime.now()))
            request_count += 1
            seconds = (datetime.now() - time_started).seconds if datetime.now() > time_started else 0
            if seconds > config.rate_limit[1]:
                request_count, time_started = (0, datetime.now())
            elif request_count >= config.rate_limit[0] and seconds < config.rate_limit[1]:
                self.abort(503)
            self.session['rate_limiter_request'] = (request_count, time_started)

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session(backend=config.session_backend)

    @webapp2.cached_property
    def messages(self):
        return self.session.get_flashes(key='_messages')

    def add_message(self, message, level=None):
        self.session.add_flash(message, level, key='_messages')

    @webapp2.cached_property
    def user(self):
        if self.user_id:
            # todo implement this your way on how you want to access your user
            return
        return None

    @webapp2.cached_property
    def user_id(self):

        return self.session.get('user_id', 0)

    @webapp2.cached_property
    def is_ajax(self):
        return self.request.headers.get('X-Requested-With', None) == 'XMLHttpRequest'

    def static_url(self, num=0):

        if not config.is_local:
            cdn_path = [str(num), str(APP_VERSION), VERSION]
            module_name = modules.get_current_module_name()
            if module_name != 'default':
                cdn_path.append(module_name)
            cdn_path.append(app_identity.get_default_version_hostname())

            return 'https://{}'.format('-dot-'.join(cdn_path))

        return 'http://{}'.format(self.request.host)

    def jinja2_factory(self, app):
        j = jinja2.Jinja2(app)
        j.environment.filters.update({
            # Set filters.
            'json_dumps': json.dumps,
            'js_time_format': utils.js_time_format
        })
        j.environment.globals.update({
            # Set global variables.
            'uri_for': self.uri_for,
            'static_url': self.static_url,
            'is_production': config.is_production,
            'is_local': config.is_local,
            'project_name': config.project_name,
            'now': datetime.now()
        })
        j.environment.tests.update({
            # Set tests.
            # ...
        })
        return j

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=self.jinja2_factory, app=self.app)

    def render_template(self, filename, base_template="base.html", **kwargs):
        kwargs.update({
            'user_id': self.user_id,
            'url': self.request.url,
            'path': self.request.path,
            'query_string': self.request.query_string,
            'base_template': base_template
        })

        if self.messages:
            kwargs['messages'] = self.messages

        self.response.headers.add_header('X-UA-Compatible', 'IE=Edge,chrome=1')
        self.response.write(self.jinja2.render_template(filename, **kwargs))

    def query_result(self, data, **kwargs):
        my_list, cursor, more = data

        futures = [d.to_client_async(**kwargs) for d in my_list]
        ndb.Future.wait_all(futures)

        web_cursor = None
        if more:
            if hasattr(cursor, 'urlsafe'):
                web_cursor = cursor.urlsafe()
            elif hasattr(cursor, 'web_safe_string'):
                web_cursor = cursor.web_safe_string

        return [future.get_result() for future in futures], web_cursor


class RpcHandler(BaseHandler):

    def post(self):
        server = jsonrpc.Server(self)
        server.handle(self.request, self.response)


class Webapp2HandlerAdapter(webapp2.BaseHandlerAdapter):

    def __call__(self, request, response, exception):
        request.route_args = {
            'exception': exception
        }
        logging.exception(exception)
        handler = self.handler(request, response)

        return handler.get()
