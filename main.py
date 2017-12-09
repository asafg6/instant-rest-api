import inspect
from wsgiref import simple_server
import falcon
import config
from model import InstantModel
from view import ViewResource, IndexResource


def make_app():
    app = falcon.API(media_type=falcon.MEDIA_JSON)
    routes = []
    import user_models
    for name, klass in inspect.getmembers(user_models,
                                          lambda x: inspect.isclass(x) and issubclass(x, InstantModel)):
        if klass == InstantModel:
            continue
        resource_model = klass()
        view = ViewResource(resource_model)
        route = '/%s' % name.lower()
        app.add_route(route, view)
        routes.append(route)
    index = IndexResource(routes)
    app.add_route('/', index)
    return app


if __name__ == '__main__':
    app = make_app()
    httpd = simple_server.make_server(config.host, config.port, app)
    httpd.serve_forever()



