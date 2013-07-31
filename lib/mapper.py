import datetime
from google.appengine.api import memcache
import logging

__author__ = 'faisal'

from google.appengine.ext import deferred, ndb
from google.appengine.runtime import DeadlineExceededError


class Mapper(object):
    prefix_key = 'mapper_'

    def __init__(self, use_cache=False):
        ndb.get_context().set_cache_policy(use_cache)
        if not use_cache:
            ndb.get_context().clear_cache()

        self.KIND = None
        self.to_put = []
        self.to_delete = []
        self.terminate = False
        # Data you wanna carry on in case of error
        self.DATA = None
        # Temporary Data that won't carry on in case of error
        self.TMP_DATA = None
        self.FILTERS = []
        self.ORDERS = []
        # implement init for different initializations
        self.init()

    def delete(self, entity):
        self.to_delete.append(entity.key)

    def update(self, entity):
        self.to_put.append(entity)

    def map(self, entity):
        """Updates a single entity.

        Implementers should return a tuple containing two iterables (to_update, to_delete).
        """

    def init(self):
        # initialize variables
        pass

    def deadline_error(self):
        # on deadline error execute
        pass

    def finish(self):
        """Called when the mapper has finished, to allow for any final work to be done."""
        pass

    def get_query(self):
        """Returns a query over the specified kind, with any appropriate filters applied."""
        q = self.KIND.query()
        for filter in self.FILTERS:
            q = q.filter(filter)
        for order in self.ORDERS:
            q = q.order(order)

        return q

    def run(self, batch_size=100, initial_data=None):
        if initial_data is None:
            initial_data = self.DATA
        """Starts the mapper running."""
        if hasattr(self, '_pre_run_hook'):
            getattr(self, '_pre_run_hook')()

        self._continue(None, batch_size, initial_data)

    def _batch_write(self):
        """Writes updates and deletes entities in a batch."""
        if self.to_put:
            ndb.put_multi(self.to_put)
            del self.to_put[:]
        if self.to_delete:
            ndb.delete_multi(self.to_delete)
            del self.to_delete[:]

    def _continue(self, cursor, batch_size, data):
        self.DATA = data
        q = self.get_query()
        if q is None:
            self.finish()
            return
        # If we're resuming, pick up where we left off last time.
        iter = q.iter(produce_cursors=True, start_cursor=cursor)
        # Keep updating records until we run out of time.
        cache_id = self.prefix_key + self.__class__.__name__
        try:
            # create a 10 minute cache
            start_time = datetime.datetime.now()
            memcache.set(cache_id, start_time, 60 * 10)
            # Steps over the results, returning each entity and its index.
            i = 0
            while iter.has_next():
                entity = iter.next()
                self.map(entity)
                # Do updates and deletes in batches.
                if (i + 1) % batch_size == 0:
                    # Record the last entity we processed.
                    self._batch_write()
                    # check if time has expired
                    if (datetime.datetime.now() - start_time).seconds > 60 * 10:
                        start_time = datetime.datetime.now()
                        memcache.set(cache_id, start_time, 60 * 10)
                i += 1
                if self.terminate:
                    break

            self._batch_write()
        except DeadlineExceededError:
            # Write any unfinished updates to the datastore.
            self._batch_write()
            self.deadline_error()
            # Queue a new task to pick up where we left off.
            deferred.defer(self._continue, iter.cursor_after(), batch_size, self.DATA)
            logging.error(self.__class__.__name__ + ' DeadlineExceedError')
            return
        self.finish()
        memcache.delete(cache_id)