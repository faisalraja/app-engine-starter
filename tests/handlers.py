import unittest
from google.appengine.ext import testbed
from webapp2_extras import jinja2
import webtest

__author__ = 'faisal'

# Correct templates path
jinja2.default_config['template_path'] = '../templates'


class AppTest(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.setup_env(app_id='app-engine-starter', CURRENT_VERSION_ID='1.1')
        self.testbed.activate()
        self.testbed.init_all_stubs()

        import main
        # todo figure out how to get it properly on ndb.toplevel
        self.app = webtest.TestApp(main.app.__dict__['__wrapped__'])

    def tearDown(self):
        self.testbed.deactivate()

    def testHomeHandler(self):
        # Get Test
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('<title>App Engine Starter</title>', response.body)

        # Post Test not logged in
        response = self.app.post('/', {'message': 'Hello'})
        # Cause if not logged in you are just redirected
        self.assertEqual(response.status_code, 302)