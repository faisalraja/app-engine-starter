import os
from google.appengine.api import app_identity
from lib import auth_provider
from authomatic.providers import oauth2, oauth1

app_id = app_identity.get_application_id()
is_local = os.environ.get('SERVER_SOFTWARE', 'Dev').startswith('Dev')
is_production = app_id == 'put-production-app-id-here'

# Restrict appspot.com put None if you don't want to restrict username/password
# This is useful if you don't want duplicate content serving on project-id.appspot.com
restricted_auth = None  # 'admin:admin'


# webapp2 configurations
# Generating random hex
# >>> import os,binascii
# >>> binascii.b2a_hex(os.urandom(32)).upper()
webapp2_config = {
    'webapp2_extras.sessions': {
        'secret_key': '-- generate a random 64 hexa decimal here per project --'
    },
}


# Remember that memcache can be evicted
# so if you have important stuff in session like carts use datastore
session_backend = 'memcache'


# Rate limiting settings
# rate_limit = (200, 60) # 200 request / minute
# rate_limit = (10000, 3600) # 10000 request / hour
rate_limit = None

# Project name for namespacing
project_name = 'App Engine Starter'

# Password Hash iterations: Change this depending on your instance class
password_iterations = 10000

# AES256 Encryption Key
encryption_key = '-- generate a random 64 characters encryption key --'

sendgrid = {
    'api_key': '-- key --',
    'from_email': 'support@your-domain-here'
}

jwt_secret = '-- generate your jwt secret --'

# 1 hour email token expiration
email_token_expire_seconds = 3600

# list of email to allow outgoing email on development mode
allowed_dev_email_recipients = [
    'support@your-domain-here',
]

# google recaptcha keys
re_captcha = {
    'key': '-- key --',
    'secret': '-- secret --'
}

# auth providers settings using authomatic
auth = {
    'twitter': {
        'class_': oauth1.Twitter,
        'consumer_key': '-- key --',
        'consumer_secret': '-- secret --',
    },

    'google': {
        'class_': auth_provider.Google,

        # Provider type specific keyword arguments:
        'short_name': 2,  # use authomatic.short_name() to generate this automatically
        'consumer_key': '-- key --',
        'consumer_secret': '-- secret --',
        'scope': ['profile', 'email']
    },

    'facebook': {

        'class_': oauth2.Facebook,

        # Facebook is an AuthorizationProvider too.
        'consumer_key': '-- key --',
        'consumer_secret': '-- secret --',

        # But it is also an OAuth 2.0 provider and it needs scope.
        'scope': ['email'],
    }
}
