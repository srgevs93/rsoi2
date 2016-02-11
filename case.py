from model import Model
from pydblite import Base
from flask import blueprints, request
from datetime import datetime
import random

app = blueprints.Blueprint('case', __name__)

class Case(Model):
    name = 'case'
    base = Base('database/' + name + '.pdl')

    def create_db(cls):
        cls.base.create('user_id', 'patient', 'status', 'datetime')

    def insert_db(cls, request):
        return cls.db().insert(user_id = request.form['user_id'],
                               patient = request.form['patient'],
                               status = request.form['status'],
                               datetime=datetime.now().isoformat())

    def update_db(cls, item, request):
        return cls.db().update(item, patient = request.form['patient'],
                               status = request.form['status'])

@app.route('/case/', methods=['GET'])
def get_cases():
    return Case.get_items(request)

@app.route('/case/', methods=['POST'])
def post_case():
    return Case.post_item(request)

@app.route('/case/<id>', methods=['GET'])
def get_case(id):
    return Case.get_item(id, request)

@app.route('/case/<id>', methods=['PUT'])
def put_case(id):
    return Case.put_item(id, request)

@app.route('/case/<id>', methods=['DELETE'])
def delete_case(id):
    return Case.delete_item(id, request)

if len(Case.db()) == 0:
    for i in range(0, 50):
        id = Case.db().insert(user_id=random.choice(range(0, 10)),
                    patient='patient{}'.format(i),
                    status=random.choice(['processing', 'finished']),
                    datetime=datetime.now().isoformat())
        print(Case(id).json())
    Case.db().commit()