import re

class Router(object):
    def __init__(self, prefix=""):
        self.rules = []
        self.prefix = prefix

    def route(self, pat):
        def decor(application):
            regex = re.compile(pat)

            self.rules.append((
                    (regex, application), # for working
                    (application.__name__, pat ) # for reporting
                    ))

            return application
        return decor

    def resolve(self, path):
        for (regex, app), info in self.rules:
            if path.startswith(self.prefix):
                # Chop off the prefix
                path = path[len(self.prefix):]

            match = regex.match(path)

            if match:
                return app, match, info

        return None, None, None

    def path_info(self, environ):
        return environ['PATH_INFO']

    def __call__(self, environ, start_response):
        path = self.path_info(environ)
        app, match, info = self.resolve(path)

        if app is not None:
            kwargs = match.groupdict()

            if kwargs:
                args = ()
            else:
                kwargs = {}
                args = match.groups()

            environ['router.kwargs'] = kwargs
            environ['router.args'] = args

            return app(environ, start_response)
        
