from google.appengine.api import users
from lib.basehandler import BaseHandler


# Check routes.py to see hot everything is routed here
from models import models


class HomeHandler(BaseHandler):
    # Handles Shouts
    def post(self):
        message = self.request.get('message')
        if not message:
            self.add_message('Add a message', 'error')
        elif not self.user_id:
            self.add_message('Please login')
        else:
            models.Shout.post(message, self.request.get('name', 'Anonymous'))

        # Redirects to home when done
        return self.redirect_to('home')

    def get(self):
        # Gets list of shouts
        # Remember that queries aren't cached, refer to my blog on query caching tips
        result, cursor, more = models.Shout.list(self.request.get('more'))
        params = {
            'shouts': result,
            'more': cursor.urlsafe() if more else ''
        }
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
