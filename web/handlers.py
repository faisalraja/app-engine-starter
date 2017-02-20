import logging
import config
from authomatic import Authomatic
from authomatic.adapters import Webapp2Adapter
from lib.basehandler import BaseHandler
from models import models


authomatic = Authomatic(config=config.auth, secret=config.session_key)


class HomeHandler(BaseHandler):

    def get(self):
        posts, cursor = self.query_result(models.Post.get_recent(self.request.get('more')))

        params = {
            'active': 'home',
            'posts': posts,
            'cursor': cursor
        }
        return self.render_template('main/index.html', **params)


class PostHandler(BaseHandler):

    def get(self):
        params = {
            'active': 'post'
        }
        return self.render_template('main/post.html', **params)


class LoginProviderHandler(BaseHandler):

    def on_login(self, result):
        if result:
            if result.error:
                self.add_message(result.error.message, 'danger')
                logging.error('Error: {}'.format(result.error.message))
                return self.redirect_to('home')
            elif result.user:
                if not (result.user.name and result.user.id):
                    result.user.update()

                self.session['user_id'] = models.User.get_user_by_oauth(result)
                return self.redirect_to('home')

    def any(self, provider):
        authomatic.login(Webapp2Adapter(self), provider, self.on_login)


class LogoutHandler(BaseHandler):

    def get(self):

        if 'user_id' in self.session:
            del self.session['user_id']

        return self.redirect(self.request.referer or '/')
