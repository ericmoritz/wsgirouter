import unittest
from wsgirouter import Router

def app1(environ, start_response):
    start_response("200 OK", [])
    return ["app1"]


def app2(environ, start_response):
    start_response("200 OK", [])
    return ["app2"]


def app3(environ, start_response):
    start_response("200 OK", [])
    return ["app3"]


class RouterTest(unittest.TestCase):
    def setUp(self):
        router = Router()

        # Route app1 by decorating it
        router.route(r"^/app1/(?P<slug>.+)/$")(app1)

        # Route app2 by decorating it
        router.route(r"^/app2/(?P<slug>.+)/$")(app2)

        # Route app3 with a args
        router.route(r"^/app3/(.+)/$")(app3)

        self.router = router

    def test_resolve(self):
        app, match, info = self.router.resolve("/app1/slug1/")
        kwargs = match.groupdict()

        self.assertEqual(app, app1)
        self.assertEqual({'slug': "slug1"}, kwargs)

        app, match, info = self.router.resolve("/app2/slug2/")
        kwargs = match.groupdict()
        self.assertEqual(app, app2)
        self.assertEqual({'slug': "slug2"}, kwargs)

    def test_call(self):
        ## Call the WSGI app using a path tha t
        environ = {}
        environ['PATH_INFO'] = "/app1/slug1/"

        result = self.router(environ, lambda s,h: None)
        
        self.assertEqual(["app1"], result)
        self.assertEqual(environ['router.kwargs'],
                         {'slug': "slug1"})
        self.assertEqual(environ['router.args'],
                         ())

        environ = {}
        environ['PATH_INFO'] = "/app3/slug3/"

        result = self.router(environ, lambda s,h: None)
        
        self.assertEqual(["app3"], result)
        self.assertEqual(environ['router.kwargs'],
                         {})
        self.assertEqual(environ['router.args'],
                         ('slug3',))

