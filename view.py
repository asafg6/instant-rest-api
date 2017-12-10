from model import ObjectNotFoundException
import falcon


def standard_response(status='OK', body={}, message=None):
    return {'status': status, 'body': body, 'message': message}


class IndexResource(object):

    def __init__(self, routes):
        self.routes = routes

    def on_get(self, req, resp):
        response = {'routes': []}
        for route in self.routes:
            response['routes'].append(route)
        resp.media = response
        resp.status = falcon.HTTP_200


class ViewResource(object):

    def __init__(self, model):
        self._model = model

    def on_get(self, req, resp):
        self._add_cors(resp)
        try:
            object_id = req.get_param('id')
            if object_id and len(req.params) == 1:  # only get by id
                found_object = self._model.get_one(object_id)
                resp.status = falcon.HTTP_200
                resp.media = standard_response(body=found_object)
            else:
                # get by filters
                sort = req.get_param('sort', default=None)
                desc = req.get_param('desc', default=False)
                if desc != False:
                    desc = True
                limit = req.get_param('limit', default=None)
                if limit is not None:
                    limit = int(limit)
                offset = int(req.get_param('offset', default=0))
                equals = {}
                non_equals = {}
                for k, v in req.params.items():
                    if k not in ['sort', 'desc', 'limit', 'offset']:
                        if v.startswith('!'):
                            non_equals[k] = v[1:]
                        else:
                            equals[k] = v
                found_objects = self._model.get(sort, desc, limit, offset, equals, non_equals)
                resp.status = falcon.HTTP_200
                resp.media = standard_response(body=found_objects)
        except ValueError:
            resp.status = falcon.HTTP_400
            resp.media = standard_response(status='ERROR', message='Wrong request syntax')
        except ObjectNotFoundException as e:
            resp.status = falcon.HTTP_404
            resp.media = standard_response(status='ERROR', message=e.msg)
        except Exception as e:
            if isinstance(e, falcon.HTTPError):
                resp.status = e.status
                resp.media = standard_response(status='ERROR', message=e.description)
            else:
                resp.status = falcon.HTTP_500
                resp.media = standard_response(status='ERROR', message='Unexpected error occurred')

    def on_post(self, req, resp):
        self._add_cors(resp)
        try:
            if len(req.params) > 0:
                resp.status = falcon.HTTP_400
                resp.media = standard_response(status='ERROR', message='query string arguments not allowed')
                return
            new_id = self._model.create(**req.media)
            resp.status = falcon.HTTP_201
            resp.media = standard_response(body={'id': new_id}, message='object created')
        except Exception as e:
            if hasattr(e, 'description') and hasattr(e, 'status'):
                resp.status = e.status
                resp.media = standard_response(status='ERROR', message=e.description)
            else:
                resp.status = falcon.HTTP_500
                resp.media = standard_response(status='ERROR', message='Unexpected error occurred')

    def on_put(self, req, resp):
        self._add_cors(resp)
        try:
            object_id = req.get_param('id', required=True)
            self._model.update(object_id, **req.media)
            new_object = self._model.get_one(object_id)
            resp.status = falcon.HTTP_202
            resp.media = standard_response(body=new_object, message="Updated")
        except ObjectNotFoundException as e:
            resp.status = falcon.HTTP_404
            resp.media = standard_response(status='ERROR', message=e.msg)
        except falcon.HTTPBadRequest:
            resp.status = falcon.HTTP_400
            resp.media = standard_response(status='ERROR', message='Must specify id in query params')
        except Exception as e:
            if isinstance(e, falcon.HTTPError):
                resp.status = e.status
                resp.media = standard_response(status='ERROR', message=e.description)
            else:
                resp.status = falcon.HTTP_500
                resp.media = standard_response(status='ERROR', message='Unexpected error occurred')

    def on_delete(self, req, resp):
        self._add_cors(resp)
        try:
            object_id = req.get_param('id', required=True)
            # we allow deletion of a few ids
            object_ids = object_id.split(',')
            self._model.delete(*object_ids)
            resp.status = falcon.HTTP_200
            resp.media = standard_response(message='Deleted')
        except ObjectNotFoundException as e:
            resp.status = falcon.HTTP_404
            resp.media = standard_response(status='ERROR', message=e.msg)
        except falcon.HTTPBadRequest:
            resp.status = falcon.HTTP_400
            resp.media = standard_response(status='ERROR', message='Must specify id in query params')
        except Exception as e:
            if isinstance(e, falcon.HTTPError):
                resp.status = e.status
                resp.media = standard_response(status='ERROR', message=e.description)
            else:
                resp.status = falcon.HTTP_500
                resp.media = standard_response(status='ERROR', message='Unexpected error occurred')

    def on_options(self, req, resp):
        self._add_cors(resp)
        resp.set_header('allow', ' DELETE, GET, POST, PUT')
        resp.status = falcon.HTTP_200

    def _add_cors(self, response):
        response.set_header('Access-Control-Allow-Origin', '*')
        response.set_header('Access-Control-Expose-Headers', 'Access-Control-Allow-Origin')
        response.set_header('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')

