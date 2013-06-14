"""
This is designed more for backend developers building quick prototypes
If you want to optimize your frontend you should probably start with
using less and having a script the merge and compress them
"""
import logging
import webapp2
import config
import routes
from google.appengine.ext import deferred, ndb
from web import errors
from lib import basehandler

app = webapp2.WSGIApplication(debug=basehandler.IS_DEV, config=config.webapp2_config, routes=routes.get_routes())


# If you want dynamic custom error handlers use below
# or just comment it out. This is useful for gracefully showing errors to users
# with all your layout in place
if not basehandler.IS_BACKEND:

    # defined custom error handlers
    class Webapp2HandlerAdapter(webapp2.BaseHandlerAdapter):

        def __call__(self, request, response, exception):
            request.route_args = {
                'exception': exception
            }
            logging.exception(exception)
            handler = self.handler(request, response)

            return handler.get()

    app.error_handlers[403] = Webapp2HandlerAdapter(errors.Error403Handler)
    app.error_handlers[404] = Webapp2HandlerAdapter(errors.Error404Handler)
    app.error_handlers[503] = Webapp2HandlerAdapter(errors.Error503Handler)
    app.error_handlers[500] = Webapp2HandlerAdapter(errors.Error500Handler)

# Make sure all ndb async futures finish
app = ndb.toplevel(app)