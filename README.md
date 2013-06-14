app-engine-starter
==================

I use this to create the basic app engine skeleton project for quick prototyping.
Most of the setup can also be used for final production app, your files should be organized
if you follow it's core setup.

**Summary of things**
  _lib_ - will hold your custom libraries, thirdparty libraries usually just go on root folder
  _models_ - all your endpoint messages and datastore models here
  _services_ - web services like cloud endpoints or your custom jsonrpc services
  _static_ - js/css/images and all other static files (templates for js html)
  _templates_ - jinja2 templates goes here
  _web_ - webpage handlers
  config.py - any configurable things on your project to easily edit later when you adjust things
  routes.py - all your routing needs for your url mapping to webpage handlers

Note that this is just a guideline, following it will just make life things easier when your app grows to hundreds of files