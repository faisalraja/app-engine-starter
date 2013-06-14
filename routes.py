from webapp2_extras.routes import RedirectRoute, PathPrefixRoute, DomainRoute
from web import admin, handlers

_routes = [
    # Sample for administering
    PathPrefixRoute('/admin',[
        RedirectRoute('/', admin.HomeHandler, name='admin-home', strict_slash=True),
    ]),

    PathPrefixRoute('/user',[
        RedirectRoute('/login', handlers.LoginHandler, name='user-login', strict_slash=True),
        # Lazy loading sample
        RedirectRoute('/logout', 'web.handlers.LogoutHandler', name='user-logout', strict_slash=True)
    ]),

    # Main Routes
    RedirectRoute('/', handlers.HomeHandler, name='home', strict_slash=True),
    # Another Lazy loading sample, will only be loaded once its routed
    RedirectRoute('/rpc', 'services.sample_jsonrpc.ApiHandler', name='rpc', strict_slash=True)
]


def get_routes():
    return _routes