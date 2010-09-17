import re

class RouteNotFound(Exception):
    def __init__(self, router, tried):
        self.router = router
        self.tried = tried

    def __str__(self):
        return "<RouteNotFound tried: %r>" % (self.tried)

class RouteMatch(object):
    def __init__(self, app, match, rest, info):
        self.app = app
        self.match = match
        self.rest = rest
        self.info = info

class Router(object):
    def __init__(self):
        self.rules = []

    def route(self, pat, methods=["GET"]):
        def decor(application):
            regex = re.compile(pat)
            self.rules.append((
                    (regex, methods, application), # for working
                    (pat,) # for reporting
                    ))

            return application
        return decor

    def resolve(self, method, path):
        tried = []
        original_path = path
        for (regex, methods, app), info in self.rules:
            if method in methods:
                match = regex.match(path)

                if match:
                    # Strip off the matched part of the path
                    rest = regex.sub("", path)
                    return RouteMatch(app, match, rest, info)
                else:
                    tried.append({'method': method, 'path': path, 'pattern': info[0], 'methods': methods})

        raise RouteNotFound(self, tried)

    def path_info(self, environ):
        return environ['PATH_INFO']

    def __call__(self, environ, start_response, path=None):
        method = environ['REQUEST_METHOD']

        if path is None:
            path = self.path_info(environ)

        result = self.resolve(method, path)

        if result.app is not None:
            kwargs = result.match.groupdict()

            if kwargs:
                args = ()
            else:
                kwargs = {}
                args = result.match.groups()

            environ['wsgiorg.routing_args'] = (args, kwargs)

            if isinstance(result.app, Router):
                return result.app(environ, start_response, path=result.rest)
            else:
                return result.app(environ, start_response)
