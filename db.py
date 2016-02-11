from pathlib import Path
from pydblite import Base

if not Path('database').exists():
    Path('database').mkdir()

client = Base('database/client.pdl')
if client.exists():
    client.open()
else:
    client.create('secret', 'redirect_uri', 'name')

authorization_code = Base('database/authorization_code.pdl')
if authorization_code.exists():
    authorization_code.open()
else:
    authorization_code.create('user_id', 'code', 'expire_time')

token = Base('database/token.pdl')
if token.exists():
    token.open()
else:
    token.create('user_id', 'access', 'expire_time', 'refresh')

if len(client) == 0:
    client.insert(secret='test_secret', redirect_uri='http://example.com', name='app1')
    client.commit()