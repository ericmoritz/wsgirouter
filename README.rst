wsgirouter is a dead simple WSGI dispatcher.  It routes a URL to a
WSGI application. `wsgirouter.Route` is itself a WSGI application, so
you can apply WSGI middleware to it.

I built this project because no WSGI URL dispatcher seemed to do what
I wanted.  They were either didn't use WSGI apps directly, too complex
(Routes) or didn't support URL variables (urlrelay, wfront).

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

  @router.route("^/entries/(.*)/"):
  def entry_detail(environ, start_response):
     args = environ['router.args']
     slug = args[0]

     # .. lookup blog entry
     start_response("200 OK", [])
     return ["Some content"]

  @router.route("^/entries/tags/(?P<tags>.+)/")
  def entries_by_tag(environ, start_response):
     kwargs = environ['router.kwargs']
     tags = kwargs['tags']

     # ... Do your magic
     start_response("200 OK", [])
     return ["Some content"]
     

  application = router


Complex Example
================
Here is an example of nesting routes::

  from blog import router as blog_router
  from wiki import router as wiki_router
  from wsgirouter import Router

  front = Router()

  front.route("^/blog")(blog_router)
  front.route("^/wiki")(wiki_router)

  application = front


Environment variables
======================
wsgirouter adds two variables to the environment for called `router.kwargs`,
and `router.args`.  These are the arguments and keyword arguments found when
matching the inner most URL pattern.


Caveat
=======
You must apply the route decorator on the outside of your decorator chain because the route decorator can only know about the function it applies to, it 
is unaware of any decorators you apply to the function after the route is
applied.  Doing this is correct::

  @router.route("^/path/")
  @my_decor
  def app(environ, start_response):
      # whatever

This is incorrect::

  @my_decor
  @router.route("^/path/")
  def app(environ, start_response):
      # whatever

In the case above, @my_decor will never be called because it wraps the
application after the router is registered with the application.



