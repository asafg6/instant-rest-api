import json
import os
import copy
import threading


class InstantModel(object):

    def __init__(self):
        dir_path = os.path.dirname(__file__)
        data_path = os.path.join(dir_path, self.__class__.__name__.lower())
        os.makedirs(data_path, exist_ok=True)
        self._lock = threading.Lock()
        self._properties = []
        self._define_properties()
        self._data_dir = data_path
        self._object_count = 0
        self._objects = {}
        self._indexes = {}
        self._read_dir()

    def _define_properties(self):
        for prop in dir(self):
            if prop.startswith('_'):
                continue
            if callable(getattr(self, prop)):
                continue
            self._properties.append(prop)

    def _read_dir(self):
        for file_name in os.listdir(self._data_dir):
            file_path = os.path.join(self._data_dir, file_name)
            with open(file_path, 'r') as fp:
                self._objects[file_name] = json.load(fp)
        self._object_count = len(self._objects)

    def _generate_id(self):
        while True:
            new_id = str(self._object_count)
            self._object_count += 1
            yield new_id

    def get(self, sort=None, desc=False, limit=None, offset=0, equals={}, non_equals={}):
        objects = []
        for object_id, object_dict in self._objects.items():
            predicates = []
            for k, v in equals.items():
                if k in self._properties:
                    value = object_dict.get(k)
                    predicates.append(str(value) == v)
            for k, v in non_equals.items():
                if k in self._properties:
                    value = object_dict.get(k)
                    predicates.append(str(value) != v)
            if all(predicates):
                objects.append(object_dict)
        if not sort:
            sorted_objects = sorted(objects, key=lambda o: o.get('id'), reverse=True)
        else:
            sorted_objects = sorted(objects, key=lambda o: o.get(sort), reverse=desc)
        if offset:
            sorted_objects = sorted_objects[offset:]
        if limit:
            sorted_objects = sorted_objects[:limit]
        return sorted_objects

    def delete(self, *object_ids):
        try:
            self._lock.acquire()
            for object_id in object_ids:
                del self._objects[object_id]
                file_path = os.path.join(self._data_dir, object_id)
                os.unlink(file_path)
        finally:
            self._lock.release()

    def update(self, object_id, **kwargs):
        found_object = copy.copy(self.get_one(object_id))
        updated = False
        for k, v in found_object.items():
            if k in kwargs:
                updated = True
                found_object[k] = kwargs.get(k)
        if updated:
            self._save(object_id, found_object)

    def get_one(self, object_id):
        if object_id in self._objects:
            return self._objects[object_id]
        raise ObjectNotFoundException(object_id)

    def create(self, **kwargs):
        gen = self._generate_id()
        object_id = next(gen)
        print(object_id)
        new_obj = {'id': object_id}
        for key in self._properties:
            new_obj[key] = kwargs.get(key)
        self._save(object_id, new_obj)
        return object_id

    def _save(self, object_id, object_to_write):
        try:
            self._lock.acquire()
            file_path = os.path.join(self._data_dir, object_id)
            with open(file_path, 'w') as fp:
                json.dump(object_to_write, fp)
            self._objects[object_id] = object_to_write
        finally:
            self._lock.release()


class ObjectNotFoundException(Exception):

    def __init__(self, object_id):
        self.msg = "Object %s not found" % object_id

