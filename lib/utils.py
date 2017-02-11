import base64
import cgi
import hashlib
import json
import re
import time
import datetime
import requests
from Crypto import Random
from Crypto.Cipher import AES
from jinja2._markupsafe import Markup
from google.appengine.api import taskqueue
import config


def nl2br(value):
    if value:
        return Markup(cgi.escape(value).replace('\n', '<br>\n'))
    return value


def pluralize(word, **kwargs):
    count = kwargs.get('count', None)
    plural_suffix = kwargs.get('plural_suffix', 's')
    singular_suffix = kwargs.get('singular_suffix', None)

    if count is not None:
        word = [count, word]
    elif not isinstance(word, list):
        word = word.split(' ')
    try:
        if int(word[0]) != 1:
            word[1] += plural_suffix
        elif singular_suffix:
            word[1] += singular_suffix
    except ValueError:  # Invalid string that's not a number.
        pass
    if count is not None:
        return word.pop()
    return ' '.join(word)


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]


def aes_encrypt(data):

    aes = AESCipher(config.encryption_key)
    return aes.encrypt(data)


def aes_decrypt(enc):

    aes = AESCipher(config.encryption_key)
    return aes.decrypt(enc)


def send_email(template, callback='default', **kwargs):
    taskqueue.add(url='/task/email', params={
        'template': template,
        'callback': callback,
        'params': json.dumps(kwargs)
    }, queue_name='slow')


def is_valid_email(email):
    if email:
        return re.match(r'[^@]+@[^@]+\.[^@]+', email)


def recaptcha_valid(response, remote_addr):
    return requests.post('https://www.google.com/recaptcha/api/siteverify', {
        'secret': config.re_captcha['secret'],
        'response': response,
        'remoteip': remote_addr
    }).json().get('success')


def to_js_time(d):

    return int(time.mktime(d.timetuple())) * 1000 if d is not None else None


def js_time_format(ts, fmt='%Y-%m-%d %H:%M:%S'):

    return datetime.datetime.fromtimestamp(int(ts / 1000)).strftime(fmt)
