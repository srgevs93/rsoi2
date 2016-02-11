from model import Model
from pydblite import Base
from flask import blueprints, request
from hashlib import sha256

app = blueprints.Blueprint('user', __name__)

class User(Model):
    name = 'user'
    base = Base('database/' + name + '.pdl')

    def create_db(cls):
        cls.base.create('login', 'password', 'name', 'email', 'phone', 'department', 'position')

    def insert_db(cls, request):
        return cls.db().insert(login=request.form['login'],
                               name=request.form['name'],
                               email=request.form['email'],
                               phone=request.form['phone'],
                               department=request.form['department'],
                               position=request.form['position'],
                               password=sha256(request.json['password'].encode('UTF-8')).hexdigest())

    def update_db(cls, item, request):
        return cls.db().update(item,
                               name=request.form['name'],
                               email=request.form['email'],
                               phone=request.form['phone'],
                               department=request.form['department'],
                               position=request.form['position'],)

    def __init__(self, id):
        super().__init__(id)
        self.data.pop('password')

@app.route('/user/', methods=['GET'])
def get_users():
    return User.get_items(request)

@app.route('/user/', methods=['POST'])
def post_user():
    return User.post_item(request)

@app.route('/user/<id>', methods=['GET'])
def get_user(id):
    return User.get_item(id, request)

@app.route('/user/<id>', methods=['PUT'])
def put_user(id):
    return User.put_item(id, request)

@app.route('/user/<id>', methods=['DELETE'])
def delete_user(id):
    return User.delete_item(id, request)

if len(User.db()) == 0:
    for i in range(0, 100):
        id = User.db().insert(login='login{}'.format(i),
                    password=sha256('password'.encode('UTF-8')).hexdigest(),
                    name='name{}'.format(i),
                    email='login{}@example.com'.format(i),
                    phone='phone{}'.format(i),
                    department='department{}'.format(i),
                    position='position{}'.format(i))
        print(User(id).json())
    User.db().commit()

