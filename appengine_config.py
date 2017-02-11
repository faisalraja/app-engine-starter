from google.appengine.ext import vendor
import os


__author__ = 'faisal'


vendor.add('ext_lib')


import requests
import requests_toolbelt.adapters.appengine
# Use the App Engine Requests adapter. This makes sure that Requests uses
# URLFetch.
requests_toolbelt.adapters.appengine.monkeypatch()
