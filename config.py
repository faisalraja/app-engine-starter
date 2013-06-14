
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


# Create your CLIENT_ID at
# https://code.google.com/apis/console
# make sure to add http://localhost:8080 if thats what you will test it on
endpoints_client_id = 'YOUR_CLIENT_ID'
