from google.appengine.api import users
from lib.basehandler import BaseHandler
from models import models


# Check routes.py to see hot everything is routed here


class HomeHandler(BaseHandler):

    def get(self):
        params = {}
        return self.render_template('main/index.html', **params)


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
