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

app.error_handlers[403] = basehandler.Webapp2HandlerAdapter(errors.Error403Handler)
app.error_handlers[404] = basehandler.Webapp2HandlerAdapter(errors.Error404Handler)
app.error_handlers[503] = basehandler.Webapp2HandlerAdapter(errors.Error503Handler)
app.error_handlers[500] = basehandler.Webapp2HandlerAdapter(errors.Error500Handler)

# Make sure all ndb async futures finish
app = ndb.toplevel(app)
