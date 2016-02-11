from hashlib import sha256
from flask import redirect, render_template, json, request, blueprints
from uuid import uuid4
from datetime import datetime, timedelta
import db

from user import User
app = blueprints.Blueprint('app', __name__)

@app.route('/oauth/authorize', methods=['GET'])
def authorize_form():
    response_type = request.args.get('response_type', None)
    client_id = request.args.get('client_id', None)
    state = request.args.get('state', None)

    if client_id is None:
        return 'missing client_id', 400

    try:
        new_client_id = int(client_id)
    except:
        return 'invalid client_id', 400

    if new_client_id not in db.client:
        print(client_id)
        return 'no id in database', 400

    if response_type is None:
        return redirect(db.client[new_client_id]['redirect_uri'] + '?error=invalid_request' +
                                                              ('' if state is None else '&state=' + state), code=302)
    if response_type != 'code':
        return redirect(db.client[new_client_id]['redirect_uri'] + '?error=unsupported_response_type' +
                                                              ('' if state is None else '&state=' + state), code=302)

    return render_template('authorize.html', state=state,
                                                  client_id=new_client_id,
                                                  client_name=db.client[new_client_id]['name'])


@app.route('/oauth/authorize', methods=['POST'])
def authorize():
    client_id = int(request.form.get('client_id'))
    login = request.form.get('login')
    password = request.form.get('password')
    state = request.form.get('state', None)

    user_db = User.db()
    if not user_db(login=login):
        return redirect(db.client[client_id]['redirect_uri'] +
                        '?error=access_denied' +
                        ('' if state is None else '&state=' + state), code=302)

    if User.db()(login=login)[0]['password'] != sha256(password.encode('UTF-8')).hexdigest():
        print (sha256(password.encode('UTF-8')).hexdigest())
        print (password)
        return redirect(db.client[client_id]['redirect_uri'] +
                        '?error=access_denied' +
                        ('' if state is None else '&state=' + state), code=302)

    code = sha256(str(uuid4()).encode('UTF-8')).hexdigest()
    db.authorization_code.insert(user_id=User.db()(login=login)[0]['__id__'],
                                 code=code,
                                 expire_time=datetime.now() + timedelta(minutes=10))
    db.authorization_code.commit()

    return redirect(db.client[client_id]['redirect_uri'] +
                    '?code=' + code +
                    ('' if state is None else '&state=' + state), code=302)

@app.route('/oauth/token', methods=['POST'])
def token():
    try:
        grant_type = request.form.get('grant_type')
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
    except KeyError:
        return json.dumps({'error': 'invalid_request'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

    try:
        client_id = int(client_id)
    except:
        client_id = None
    if client_id not in db.client or db.client[client_id]['secret'] != client_secret:
        print (client_id)
        print (client_secret)
        return json.dumps({'error': 'invalid_client'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

    if grant_type == 'authorization_code':
        try:
            code = request.form.get('code')
        except KeyError:
            return json.dumps({'error': 'invalid_request'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

        if not db.authorization_code(code=code) or db.authorization_code(code=code)[0]['expire_time'] < datetime.now():
            return json.dumps({'error': 'invalid_grant'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

        user_id = db.authorization_code(code=code)[0]['user_id']

        db.authorization_code.delete(db.authorization_code(code=code))
        db.authorization_code.commit()
    elif grant_type == 'refresh_token':
        try:
            refresh_token = request.form.get('refresh_token')
        except KeyError:
            return json.dumps({'error': 'invalid_request'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

        if not db.token(refresh=refresh_token):
            return json.dumps({'error': 'invalid_grant'}), 400, {
                'Content-Type': 'application/json;charset=UTF-8',
            }

        user_id = db.token(refresh=refresh_token)[0]['user_id']

        db.token.delete(db.token(refresh=refresh_token))
        db.token.commit()
    else:
        return json.dumps({'error': 'unsupported_grant_type'}), 400, {
            'Content-Type': 'application/json;charset=UTF-8',
        }

    access_token = sha256(str(uuid4()).encode('UTF-8')).hexdigest()
    expire_time = datetime.now() + timedelta(hours=1)
    refresh_token = sha256(str(uuid4()).encode('UTF-8')).hexdigest()
    db.token.insert(user_id=user_id,
                    access=access_token,
                    expire_time=expire_time,
                    refresh=refresh_token)
    db.token.commit()

    return json.dumps({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': 3600,
        'refresh_token': refresh_token,
    }), 200, {
        'Content-Type': 'application/json;charset=UTF-8',
        'Cache-Control': 'no-store',
        'Pragma': 'no-cache',
    }

@app.route('/register', methods=['GET'])
def register_form():
    return render_template('user.html', user=None)

def check_auth(request):
   # return '0'
    access_token = request.headers.get('Authorization', '')[len('Bearer '):]
    if not db.token(access=access_token) or db.token(access=access_token)[0]['expire_time'] < datetime.now():
        return None


    return db.token(access=access_token)[0]['user_id']