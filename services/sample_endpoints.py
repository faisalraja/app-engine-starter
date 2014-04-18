import logging
import endpoints
from google.appengine.api import oauth
from google.appengine.api.oauth import NotAllowedError
from google.appengine.ext import deferred
from protorpc import remote, message_types
import config
from mappers import demo
from models import messages

__author__ = 'faisal'


@endpoints.api(name='demo',
               version='v1',
               description='Sample Endpoints Api',
               allowed_client_ids=[config.endpoints_client_id, endpoints.API_EXPLORER_CLIENT_ID])
class ApiService(remote.Service):

    @endpoints.method(response_message=messages.User,
                      name='user.email',
                      path='user/email')
    def user_get_email(self, request):
        user = endpoints.get_current_user()
        if user is None:
            raise endpoints.UnauthorizedException('Invalid token.')

        return messages.User(email=user.email())

    @endpoints.method(messages.HelloRequest,
                      messages.HelloList,
                      name='hello',
                      path='hello')
    def hello(self, request):

        return messages.HelloList(words=[str(request.world) for i in range(request.limit)])

    @endpoints.method(name='mappers.deleteShouts')
    def delete_shouts(self, request):

        # This sample runs it in the mappers backend, with 100 batches, the more things you do in map
        # the smaller the batch should be to avoid duplicate runs on failures
        deferred.defer(demo.DeleteAllShout().run, 100)

        return message_types.VoidMessage()