import cerberus
from cerberus.errors import BasicErrorHandler
from lib.jsonrpc import ServerException


class CustomErrorHandler(BasicErrorHandler):

    def __init__(self, tree=None, messages=None):
        super(CustomErrorHandler, self).__init__(tree)
        self.custom_messages = messages or {}

    def format_message(self, field, error):
        tmp = self.custom_messages
        for x in error.schema_path:
            try:
                tmp = tmp[x]
            except KeyError:
                return super(CustomErrorHandler, self).format_message(field, error)
        if isinstance(tmp, dict):  # if "unknown field"
            return super(CustomErrorHandler, self).format_message(field, error)
        else:
            return tmp


class ValidationError(ServerException):

    def __init__(self, data=None, message='Validation error', code=-32001):
        Exception.__init__(self, message)
        self.data = data
        self.code = code


def build(schema, messages=None):
    v = cerberus.Validator(
        schema,
        error_handler=CustomErrorHandler(messages=messages)
    )
    return v
