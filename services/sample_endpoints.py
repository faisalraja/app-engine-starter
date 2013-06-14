import logging
from google.appengine.api import oauth
from google.appengine.api.oauth import NotAllowedError
from google.appengine.ext import endpoints
from protorpc import remote
import config
from models import messages

__author__ = 'faisal'


@endpoints.api(name='demo',
               version='v1',
               description='Sample Endpoints Api',
               allowed_client_ids=[config.endpoints_client_id, endpoints.API_EXPLORER_CLIENT_ID])
class ApiService(remote.Service):

    @endpoints.method(response_message=messages.User,
                      name='user.email',
                      path='user')
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