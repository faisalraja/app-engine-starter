from protorpc import messages

__author__ = 'faisal'


class User(messages.Message):
    email = messages.StringField(100)


class HelloRequest(messages.Message):
    world = messages.StringField(50, default='world')
    limit = messages.IntegerField(5, default=1)


class HelloList(messages.Message):
    words = messages.StringField(50, repeated=True)