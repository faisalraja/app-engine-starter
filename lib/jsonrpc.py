import json, inspect
import logging
import traceback
import uuid
import urllib2
import sys
from google.appengine.ext import ndb

__author__ = 'faisal'

"""
Server Usage:
server = Server(YourClass())
server.handler(webapp2.request, webapp2.response)

Client Usage: (Passing headers help with authorization cookies)
client = Client('http://path/to/rpc', webapp2.request.headers)
client.method_name(args)
Batch usage:
with client:
    m1 = client.method_1(args)
    m2 = client.method_2(args)
    
with client:
    m3 = client.method_1(diff_args)
    m4 = client.method_2(diff_args)

Then call to get the result
print m1() - if this is an async client, it will batch the call on your first result call
print m2()

If you are doing large number of batches, and you are done with the results call clear_batch_result()
to free up memory

ClientAsync is same as client except it returns a future so you need to call get_result() for it.
Also uses ndb context so it will be auto batched with other ndb async calls.

Batch in ClientAsync works the same way, there is no need to call get_result() on anything. It will auto batch
everything in your first result call.
"""

VERSION = '2.0'
ERROR_MESSAGE = {
    -32700: 'Parse error',
    -32600: 'Invalid Request',
    -32601: 'Method not found',
    -32602: 'Invalid params',
    -32603: 'Internal error'
}


class ServerException(Exception):
    """
    code -32000 to -32099 for custom server errors
    """

    def __init__(self, data=None, message='Server error', code=-32000):
        Exception.__init__(self, message)
        self.data = data
        self.code = code


class Server(object):
    response = None

    def __init__(self, obj):
        self.obj = obj

    def error(self, id, code, message='Server error', data=None):
        error_value = {'code': code, 'message': ERROR_MESSAGE.get(code, message)}
        if data:
            error_value['data'] = data
        return self.result({'jsonrpc': VERSION, 'error': error_value, 'id': id})

    def result(self, result):
        if self.response is None:
            return result
        else:
            if hasattr(self.response, 'headers'):
                self.response.headers['Content-Type'] = 'application/json'
            if hasattr(self.response, 'write'):
                self.response.write(json.dumps(result))

    @ndb.tasklet
    def handle(self, request, response=None, data=None):
        self.response = response

        if not data:
            try:
                data = json.loads(request.body)
            except ValueError, e:
                raise ndb.Return(self.error(None, -32700))
        # batch calls
        if isinstance(data, list):
            batch_result = yield [self.handle(None, None, d) for d in data]
            self.response = response
            raise ndb.Return(self.result(batch_result))

        if data.get('jsonrpc') != '2.0':
            raise ndb.Return(self.error(-32600))

        if 'id' in data:
            id = data['id']
        else:
            id = None

        if 'method' in data:
            method = data['method']
        else:
            raise ndb.Return(self.error(id, -32600))

        if 'params' in data:
            params = data['params']
        else:
            params = {}

        if method in vars(self.obj.__class__) and not method.startswith('_'):
            method = getattr(self.obj, method)
        else:
            raise ndb.Return(self.error(id, -32601))

        method_info = inspect.getargspec(method)
        arg_len = len(method_info.args)
        def_len = 0
        if method_info.defaults is not None:
            def_len = len(method_info.defaults)

        # Check if params is valid and remove extra params
        named_params = not isinstance(params, list)
        invalid_params = False
        clean_params = {}
        if arg_len > 1 and params is None:
            invalid_params = True
        elif named_params:
            if arg_len > 1:
                req_len = arg_len - def_len
                for i in range(1, arg_len):
                    arg = method_info.args[i]
                    if arg in params:
                        clean_params[arg] = params[arg]
                    elif i < req_len:
                        invalid_params = True
        else:
            if len(params) + 1 < arg_len - def_len:
                invalid_params = True

        if invalid_params:
            raise ndb.Return(self.error(id, -32602))
        try:
            if named_params:
                result = method(**clean_params)
            else:
                result = method(*params)
            if isinstance(result, ndb.Future):
                result = yield result
        except ServerException as e:
            raise ndb.Return(self.error(id, e.code, e.message, e.data))
        except:
            logging.error(''.join(traceback.format_exception(*sys.exc_info())))
            raise ndb.Return(self.error(id, -32603))

        if id is not None:
            raise ndb.Return(self.result({'result': result, 'id': id, 'jsonrpc': VERSION}))


class Client(object):
    def __init__(self, uri, headers=None):
        self.uri = uri
        self.headers = headers or {}
        self.batch = None
        self.batch_results = {}

    def __getattr__(self, method):

        def default(*args, **kwargs):
            params = {}
            if len(kwargs) > 0:
                params = kwargs
            elif len(args) > 0:
                params = args

            return self.request(method, params)

        return default

    def __enter__(self):
        self.batch = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        batch = self.batch
        self.batch = None
        self.request(None, None, batch=batch)

    def clear_batch_results(self):
        self.batch_results = {}

    def set_batch_results(self, result):
        for r in result:
            if r.get('id'):
                self.batch_results[r['id']] = r.get('result')

    def batch_result(self, result_id):

        def result():
            return self.batch_results.get(result_id)

        return result

    def request(self, method, params, batch=None):
        parameters = batch or {
            'id': str(uuid.uuid4()),
            'method': method,
            'params': params,
            'jsonrpc': VERSION
        }

        if self.batch is not None and batch is None:
            self.batch.append(parameters)
            return self.batch_result(parameters['id'])

        data = json.dumps(parameters)

        headers = {
            "Content-Type": "application/json"
        }
        headers = dict(headers.items() + self.headers.items())
        req = urllib2.Request(self.uri, data, headers)

        response = urllib2.urlopen(req).read()
        try:
            result = json.loads(response)
        except ValueError:
            raise ServerException(ERROR_MESSAGE[-32700], code=-32700)

        if batch is not None:
            self.set_batch_results(result)
        elif 'error' in result:
            raise ServerException(
                message='{} Code: {}'.format(result['error']['message'], result['error']['code']),
                code=result['error']['code']
            )
        elif parameters['id'] == result['id'] and 'result' in result:
            return result['result']


class ClientAsync(object):
    def __init__(self, uri, headers=None):
        self.uri = uri
        self.headers = headers or {}
        self.batch = None
        self.batch_results = {}
        self.pending_batch = []

    def __enter__(self):
        self.batch = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        batch = self.batch
        self.batch = None
        self.pending_batch.append(self.request_async(None, None, batch=batch))

    def clear_batch_results(self):
        self.batch_results = {}

    def set_batch_results(self, result):
        for r in result:
            if r.get('id'):
                self.batch_results[r['id']] = r.get('result')

    def batch_result(self, result_id):

        def result():
            if self.pending_batch:
                ndb.Future.wait_all(self.pending_batch)
                [batch.get_result() for batch in self.pending_batch]
                self.pending_batch = []

            return self.batch_results.get(result_id)

        return result

    def __getattr__(self, method):

        @ndb.tasklet
        def default_async(*args, **kwargs):
            params = {}
            if len(kwargs) > 0:
                params = kwargs
            elif len(args) > 0:
                params = args

            req = yield self.request_async(method, params)
            raise ndb.Return(req)

        def default(*args, **kwargs):
            params = {}
            if len(kwargs) > 0:
                params = kwargs
            elif len(args) > 0:
                params = args

            return self.request_async(method, params).get_result()

        return default_async if self.batch is None else default

    @ndb.tasklet
    def request_async(self, method, params, batch=None):
        parameters = batch or {
            'id': str(uuid.uuid4()),
            'method': method,
            'params': params,
            'jsonrpc': VERSION
        }

        if self.batch is not None and batch is None:
            self.batch.append(parameters)
            raise ndb.Return(self.batch_result(parameters['id']))

        data = json.dumps(parameters)

        headers = {
            "Content-Type": "application/json"
        }
        headers = dict(headers.items() + self.headers.items())

        ctx = ndb.get_context()
        response = yield ctx.urlfetch(self.uri, data, 'post', headers)

        try:
            result = json.loads(response.content)
        except:
            raise ServerException(ERROR_MESSAGE[-32700], code=-32700)

        if batch is not None:
            self.set_batch_results(result)
        elif 'error' in result:
            raise ServerException(
                message='{} Code: {}'.format(result['error']['message'], result['error']['code']),
                code=result['error']['code']
            )
        elif parameters['id'] == result['id'] and 'result' in result:
            raise ndb.Return(result['result'])
