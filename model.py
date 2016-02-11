from pathlib import Path
from pydblite import Base
import json
import math
import oauth

def url(name):
    return '/' + name + '/'

class Model:
    name = ''
    data = {}
    base = Base('')


    def __init__(self, id):
        self.data = self.db()[id].copy()
        self.data['id'] = self.data.pop('__id__')
        self.data.pop('__version__')

    @classmethod
    def create_db(cls):
        pass

    @classmethod
    def insert_db(cls, request):
        pass

    @classmethod
    def update_db(cls, item, request):
        pass

    @classmethod
    def db(cls):
        if not Path('database').exists():
            Path('database').mkdir()

        if not cls.base.exists():
            cls.create_db(cls)
        try:
            cls.base.get_indices()
        except:
            cls.base.open()
        return cls.base

    def map(self):
        return self.data

    def json(self):
        return Model.jsonify(self.map())

    @classmethod
    def get_json_page(cls, page, per_page):
        items = []
        for i, elem in enumerate(cls.db()):
            if i < page * per_page:
                continue
            if i >= (page + 1) * per_page:
                break
            item = cls(elem['__id__'])
            items.append(item.map())

        return Model.jsonify({
            'items': items,
            'per_page': per_page,
            'page': page,
            'page_count': math.ceil(len(cls.db()) / per_page)
        })

    @staticmethod
    def jsonify(item):
        return json.dumps(item, indent=4), 200, {
            'Content-Type': 'application/json;charset=UTF-8',
        }


    @classmethod
    def check_id(cls, id):
        try:
            int_id = int(id)
        except:
            return '', 400

        try:
            if int_id not in cls.db():
                raise Exception()
        except:
            return '', 404

        return int_id

    @classmethod
    def get_items(cls, request):
        try:
            per_page = int(request.args.get('per_page', 20))
            if per_page < 20 or per_page > 100:
                raise Exception()
            page = int(request.args.get('page', 0))
            if page < 0 or page > len(cls.db()) // per_page:
                raise Exception()

        except:
            return '', 400

        return cls.get_json_page(page, per_page)

    @classmethod
    def post_item(cls, request):
        if oauth.check_auth(request) is None:
            return '', 401
	
        try:
            id = cls.insert_db(cls, request)
            cls.db().commit()
        except:
            return '', 400

        return '', 201, {
            'Location': '/' + cls.name + '/{}'.format(id)
        }

    @classmethod
    def get_item(cls, id, request):
        if oauth.check_auth(request) is None:
            return '', 401

        check = cls.check_id(id)
        if not isinstance(check, int):
            return check

        return cls(check).json()

    @classmethod
    def delete_item(cls, id, request):
        if oauth.check_auth(request) is None:
            return '', 401
	
        check = cls.check_id(id)
        if not isinstance(check, int):
            return check

        try:
            cls.db().delete(cls.db()[check])
            cls.db().commit()
        except:
            return '', 400

        return '', 200

    @classmethod
    def put_item(cls, id, request):
        if oauth.check_auth(request) is None:
            return '', 401

        check = cls.check_id(id)
        if not isinstance(check, int):
            return check

        try:
            cls.update_db(cls, cls.db()[check], request)
            cls.db().commit()
        except:
            return '', 400

        return '', 200




