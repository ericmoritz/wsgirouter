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


def save(environ, start_response):
    start_response("200 OK", [])
    return ["save"]


class RouterTest(unittest.TestCase):
    def setUp(self):
        router = Router()

        # Route app1 by decorating it
        router.route(r"^/app1/(?P<slug>.+)/$")(app1)

        # Route app2 by decorating it
        router.route(r"^/app2/(?P<slug>.+)/$")(app2)

        # Route app3 with a args
        router.route(r"^/app3/(.+)/$")(app3)

        # Route app3 as a POST or PUT to test if given the same URL with
        # a differnt method that it'll return the correct WSGI application
        router.route(r"^/app3/(.+)/$", methods=["POST", "PUT"])(save)

        self.router = router

    def test_resolve(self):
        result = self.router.resolve("GET", "/app1/slug1/")
        app, match = result.app, result.match
        kwargs = match.groupdict()

        self.assertEqual(app, app1)
        self.assertEqual({'slug': "slug1"}, kwargs)

        result = self.router.resolve("GET", "/app2/slug2/")
        app, match = result.app, result.match
        kwargs = match.groupdict()
        self.assertEqual(app, app2)
        self.assertEqual({'slug': "slug2"}, kwargs)

        result = self.router.resolve("GET", "/app3/slug3/")
        app, match = result.app, result.match
        args = match.groups()
        self.assertEqual(app, app3)
        self.assertEqual(("slug3", ), args)

        for method in ["POST", "PUT"]:
            result = self.router.resolve("POST", "/app3/slug3/")
            app, match = result.app, result.match
            args = match.groups()
            self.assertEqual(app, save)
            self.assertEqual(("slug3", ), args)

    def test_call(self):
        ## Call the WSGI app using a path tha t
        environ = {}
        environ['HTTP_METHOD'] = "GET"
        environ['PATH_INFO'] = "/app1/slug1/"

        result = self.router(environ, lambda s,h: None)
        
        self.assertEqual(["app1"], result)
        self.assertEqual(environ['router.kwargs'],
                         {'slug': "slug1"})
        self.assertEqual(environ['router.args'],
                         ())

        environ = {}
        environ['HTTP_METHOD'] = "GET"
        environ['PATH_INFO'] = "/app3/slug3/"

        result = self.router(environ, lambda s,h: None)
        
        self.assertEqual(["app3"], result)
        self.assertEqual(environ['router.kwargs'],
                         {})
        self.assertEqual(environ['router.args'],
                         ('slug3',))


        environ = {}
        environ['HTTP_METHOD'] = "PUT"
        environ['PATH_INFO'] = "/app3/slug3/"

        result = self.router(environ, lambda s,h: None)
        
        self.assertEqual(["save"], result)
        self.assertEqual(environ['router.kwargs'],
                         {})
        self.assertEqual(environ['router.args'],
                         ('slug3',))


class TestComplexRouting(unittest.TestCase):
    def setUp(self):
        front = Router()

        # Create two seperate routes for nested routes
        route1 = Router()
        route1.route("^/app1/(?P<slug>.+)/")(app1)

        route2 = Router()
        route2.route("^/app2/(?P<slug>.+)/")(app2)
        
        front.route(r"^/route1")(route1)
        front.route(r"^/route2")(route2)

        self.front = front

    def test_nested_routes(self):
        environ = {}


        # Call front with the two nested URLs

        environ = {}
        environ['HTTP_METHOD'] = "GET"
        environ['PATH_INFO'] = "/route1/app1/slug1/"
        result = self.front(environ, lambda s,h: None)
        self.assertEqual(['app1'], result)
        self.assertEqual(environ['router.kwargs'],
                         {'slug': 'slug1'})
        self.assertEqual(environ['router.args'], ())

        environ = {}
        environ['HTTP_METHOD'] = "GET"
        environ['PATH_INFO'] = "/route2/app2/slug2/"
        result = self.front(environ, lambda s,h: None)
        self.assertEqual(['app2'], result)
        self.assertEqual(environ['router.kwargs'],
                         {'slug': 'slug2'})
        self.assertEqual(environ['router.args'], ())
