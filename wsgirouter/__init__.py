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

    def route(self, pat):
        def decor(application):
            regex = re.compile(pat)
            self.rules.append((
                    (regex, application), # for working
                    (pat,) # for reporting
                    ))

            return application
        return decor

    def resolve(self, path):
        tried = []
        original_path = path
        for (regex, app), info in self.rules:
            match = regex.match(path)

            if match:
                # Strip off the matched part of the path
                rest = regex.sub("", path)
                return RouteMatch(app, match, rest, info)
            else:
                tried.append({'path': path, 'pattern': info[0]})

        raise RouteNotFound(self, tried)

    def path_info(self, environ):
        if "router.path" in environ:
            return environ['router.path']
        else:
            return environ['PATH_INFO']

    def __call__(self, environ, start_response):
        path = self.path_info(environ)
        result = self.resolve(path)

        if result.app is not None:
            kwargs = result.match.groupdict()

            if kwargs:
                args = ()
            else:
                kwargs = {}
                args = result.match.groups()

            environ['router.kwargs'] = kwargs
            environ['router.args'] = args
            environ['router.path'] = result.rest

            return result.app(environ, start_response)
