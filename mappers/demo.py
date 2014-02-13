import datetime
import logging
from lib.mapper import Mapper
from models import models

__author__ = 'faisal'


# This will contain processing of filtered datastore models
# This mapper can be executed on frontends or backends and it will handle deadlineexceed errors
# Look at jsonrpc or cloudendpoints on how it's used at services/sample_*

# Mapper for deleting 15 days old shouts
class DeleteOldShout(Mapper):

    def init(self):
        self.kind = models.Shout
        self.filters = [models.Shout.created < datetime.datetime.now() - datetime.timedelta(days=15)]

    def map(self, shout):

        logging.info('Deleting %s' % shout.message)

        self.delete(shout)


class DeleteAllShout(Mapper):

    def init(self):
        self.kind = models.Shout

    def map(self, shout):

        logging.info('Deleting %s' % shout.message)

        self.delete(shout)