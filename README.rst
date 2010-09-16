wsgirouter is a dead simple WSGI dispatcher.  It routes a URL to a WSGI application. `wsgirouter.Route` is itself a WSGI
application, so you can apply WSGI middleware to it.


Usage
======
The usage is simple::

  from wsgirouter import Router
  router = Router()

  @router.route("^/entries/")
  def blog_entries(environ, start_response):
     # ... do your WSGI app
     start_response("200 OK", [])
     return ["Some content"]

  @route.route("^/entries/(.*)/"):
  def entry_detail(environ, start_response):
     args = environ['router.args']
     slug = args[0]

     # .. lookup blog entry
     start_response("200 OK", [])
     return ["Some content"]
