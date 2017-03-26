import logging
from lib.basehandler import RpcHandler
from google.appengine.ext import deferred, ndb
from lib.jsonrpc import ServerException
import models


class ApiHandler(RpcHandler):

    def save_post(self, data):

        if not self.user_id:
            raise ServerException('Access denied')

        post = models.Post.save_post(self.user_id, data)
        return post.to_client()
