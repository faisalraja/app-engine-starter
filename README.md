app-engine-starter
==================

I use this to create the basic app engine skeleton project for quick prototyping.
Most of the setup can also be used for final production app, your files should be organized
if you follow it's core setup.

Summary of things::

    lib/ - will hold your custom libraries, thirdparty libraries usually just go on root folder
    models/ - all your endpoint messages and datastore models here
    services/ - web services like cloud endpoints or your custom jsonrpc services
    mappers/ - model long tasks goes here for scripting or any task like actions
    static/ - js/css/images and all other static files (templates for js html)
    templates/ - jinja2 templates goes here
    web/ - webpage handlers
    tests/ - unit testing tests goes here
    config.py - any configurable things on your project to easily edit later when you adjust things
    routes.py - all your routing needs for your url mapping to webpage handlers

Note that this is just a guideline, following it will just make life things easier when your app grows to hundreds of files