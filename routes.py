from webapp2_extras.routes import RedirectRoute, PathPrefixRoute, DomainRoute
from services import rpc
from web import admin, handlers, email

_routes = [
    PathPrefixRoute('/admin',[
        RedirectRoute('/', admin.HomeHandler, name='admin-home', strict_slash=True),
    ]),

    PathPrefixRoute('/task', [
        RedirectRoute('/email', email.EmailHandler, name='task-email', strict_slash=True),
    ]),

    PathPrefixRoute('/user',[
        RedirectRoute('/login', handlers.LoginHandler, name='user-login', strict_slash=True),
        RedirectRoute('/login/<provider>', handlers.LoginProviderHandler, name='login-provider',
                      strict_slash=True, handler_method='any'),
        RedirectRoute('/logout', handlers.LogoutHandler, name='user-logout', strict_slash=True)
    ]),

    # Main Routes
    RedirectRoute('/', handlers.HomeHandler, name='home', strict_slash=True),
    RedirectRoute('/rpc', rpc.ApiHandler, name='rpc', strict_slash=True)
]


def get_routes():
    return _routes
