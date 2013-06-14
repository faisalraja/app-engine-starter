from google.appengine.ext import endpoints
from services.sample_endpoints import ApiService

__author__ = 'faisal'


# Now create the server and see how its added in app.yaml
# Please refer to the official docs on how to generate client libraries at
# https://developers.google.com/appengine/docs/python/endpoints/gen_clients
# Check base.html for js tests
application = endpoints.api_server([ApiService], restricted=False)