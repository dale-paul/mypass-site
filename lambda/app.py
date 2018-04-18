import json
import os
import time
import datetime
import string
import random
from chalicelib import kmscrypto, dynamo
from chalice import Chalice, Response, BadRequestError

app = Chalice(app_name='password-site')
app.debug = True

@app.route('/{key}', methods=['GET'], cors=True)
def index(key):
    secret = getSecret(key)
    if ( secret ):
        return {'secret': secret}
    return Response(body='secret not found',status_code=400, headers={'Content-Type' : 'text/plain'})

@app.route('/', methods=['PUT'], cors=True)
def createShare():
    data = app.current_request.json_body
    try:
        secret = data['secret']
        ttl = data['ttl']
        return storeSecret(secret,ttl)
    except Exception as ex:
        print(ex)
        return Response(body=str(ex),status_code=500, headers={'Content-Type' : 'text/plain'})

# for debugging
@app.route('/request', methods=['GET','PUT'], cors=True)
def request():
    return app.current_request.to_dict()

#Create a 32 bit random character string as our key
def id_generator():
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))

#turn our TTL (in seconds) into epoch time
def ttl2epoch(ttl):
    return int(time.time())+int(ttl)

#convert epoch time to string
def epoch2String(epoch):
    return datetime.datetime.utcfromtimestamp(epoch).isoformat()+'Z'

def getSecret(key):
    crypt = kmscrypto.Crypto(os.environ["kmskey"])
    db = dynamo.SecretDB(os.environ["table"])
    #guard time by creating current epoch time and using it for conditional retrieval
    now = ttl2epoch(0)
    item = db.getItem(key,now)
    if (item):
        return crypt.decrypt(item['secret'])
    return ''
    
def storeSecret(secret,ttl):
    crypt = kmscrypto.Crypto(os.environ["kmskey"])
    db = dynamo.SecretDB(os.environ["table"])
    key = id_generator()
    epoch = ttl2epoch(ttl)
    print(epoch)
    expirey = epoch2String(epoch)
    data = crypt.encrypt(secret)
    url = ''.join([os.environ["hosturl"],'/#/', key])
    db.putItem(key,epoch,data,expirey)
    return {"url": url, "expires" : expirey, "key" : key}

if __name__ == "__main__":
    os.environ["hosturl"] = 'http://reflectiveinc.net'
    os.environ["kmskey"] = "password-site"
    os.environ["table"] = 'secrets'
    rc = storeSecret("this is my secret",300)
    print(rc)
    key = rc['key']
    secret1 = getSecret(key)
    print(secret1)
    secret2 = getSecret(key)
    if ( secret2):
        print(secret2)
    else:
        print('no secret')