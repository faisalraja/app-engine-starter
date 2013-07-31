import datetime
import logging
from lib.mapper import Mapper
from models import models

__author__ = 'faisal'


# Let's put this here for now
# This will contain processing of filtered datastore models
# You can separate this if it outgrows your needs to mappers/your_mapper.py
# This mapper can be executed on frontends or backends and it will handle deadlineexceed errors


# Mapper for deleting 15 days old shouts
class DeleteShout(Mapper):

    def init(self):

        self.FILTERS = [models.Shout.created < datetime.datetime.now() - datetime.timedelta(days=15)]

    def map(self, shout):

        logging.info('Deleting %s' % shout.message)

        self.delete(shout)


# You can execute this from anywhere in your code with deferred library by
# This sample runs it in the mappers backend, with 100 batches, the more things you do in map
# the smaller the batch should be to avoid duplicate runs on failures
# from google.appengine.ext import deferred
# deferred.defer(DeleteShout.run, 100, _target='mappers')