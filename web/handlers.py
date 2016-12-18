import logging
import uuid

import config
from authomatic import Authomatic
from authomatic.adapters import Webapp2Adapter
from google.appengine.api import users
from lib.basehandler import BaseHandler
from models import models


authomatic = Authomatic(config=config.auth, secret=str(uuid.uuid4()))


class HomeHandler(BaseHandler):

    def get(self):
        params = {}
        return self.render_template('main/index.html', **params)


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
                logging.debug('UserId: {} Login Data: {}'.format(self.session['user_id'], result.user.data))
                return self.redirect_to('app')

    def any(self, provider):
        authomatic.login(Webapp2Adapter(self), provider, self.on_login)


class LoginHandler(BaseHandler):

    def get(self):
        # hold referer to redirect back
        referer = self.request.referer or '/'
        if self.request.path not in referer:
            self.session['referer'] = referer

        referer = self.session.get('referer', '/')

        if self.user_id:
            self.redirect(referer)
        else:
            user = users.get_current_user()
            if user:
                self.session['user_id'] = user.user_id()
                self.redirect(str(referer))
            else:
                self.redirect(users.create_login_url(self.request.path_url))
        return


class LogoutHandler(BaseHandler):

    def get(self):

        if 'user_id' in self.session:
            del self.session['user_id']

        self.redirect(users.create_logout_url(self.request.referer or '/'))
        return
