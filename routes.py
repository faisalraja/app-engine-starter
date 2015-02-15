from webapp2_extras.routes import RedirectRoute, PathPrefixRoute, DomainRoute
from services import sample_jsonrpc
from web import admin, handlers

_routes = [
    PathPrefixRoute('/admin',[
        RedirectRoute('/', admin.HomeHandler, name='admin-home', strict_slash=True),
    ]),

    PathPrefixRoute('/user',[
        RedirectRoute('/login', handlers.LoginHandler, name='user-login', strict_slash=True),
        RedirectRoute('/logout', handlers.LogoutHandler, name='user-logout', strict_slash=True)
    ]),

    # Main Routes
    RedirectRoute('/', handlers.HomeHandler, name='home', strict_slash=True),
    RedirectRoute('/rpc', sample_jsonrpc.ApiHandler, name='rpc', strict_slash=True)
]


def get_routes():
    return _routes