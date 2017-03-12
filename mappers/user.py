import datetime
import logging
from lib.mapper import Mapper
import models

__author__ = 'faisal'


# This will contain processing of filtered datastore models
# This mapper can be executed on frontends or backends and it will handle deadlineexceed errors

# Mapper for deleting 15 days old users
class DeleteOldUser(Mapper):

    def init(self):
        self.kind = models.User
        self.filters = [models.User.created < datetime.datetime.now() - datetime.timedelta(days=15)]

    def map(self, user):

        logging.info('Deleting {}'.format(user))

        self.delete(user)


class DeleteAllUser(Mapper):

    def init(self):
        self.kind = models.User

    def map(self, user):

        logging.info('Deleting {}'.format(user))

        self.delete(user)
