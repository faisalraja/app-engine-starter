import time
import logging
import os
import threading

LOCAL = threading.local()
CACHE = {}

STATS = {
    'hits': 0,
    'miss': 0,
    'keys_count': 0
}

CONFIG = {
    'timeout': None
}

DEBUG = os.environ.get('SERVER_SOFTWARE').startswith('Devel')


def debug(message):
    if DEBUG:
        logging.debug('Cache: {}'.format(message))


def get(key):
    if key not in CACHE:
        STATS['miss'] += 1
        debug('Missed key {}'.format(key))
        return None
    
    value, expiry = CACHE[key]
    current_timestamp = time.time()

    if expiry is None or current_timestamp < expiry:
        STATS['hits'] += 1
        debug('Found key {}'.format(key))
        return value
    else:
        STATS['miss'] += 1
        debug('Expired key {}'.format(key))
        delete(key)
        return None


def set(key, value, expiry=None):
    updated = True
    if key not in CACHE:
        STATS['keys_count'] += 1
        updated = False

    if expiry is None:
        expiry = CONFIG['timeout']

    if expiry is not None:
        expiry = time.time() + int(expiry)
    
    try:
        CACHE[key] = (value, expiry)
        debug('Set key {} expires {} updated: {}'.format(key, expiry, updated))
    except MemoryError:
        debug('Memory error for setting key {}'.format(key))
 

def delete(key):
    if key in CACHE:
        STATS['keys_count'] -= 1
        debug('Deleted key {}'.format(key))
        del CACHE[key]
    else:
        debug('Delete key {} failed'.format(key))


def flush():
    CACHE.clear()
    STATS['keys_count'] = 0


def local_get(key):
    if hasattr(LOCAL, key):
        return getattr(LOCAL, key)

    return None


def local_set(key, value):
    setattr(LOCAL, key, value)


def local_delete(key):
    if hasattr(LOCAL, key):
        delattr(LOCAL, key)
