import base64
import json
import sys
import time

import requests
from atomic_int import AtomicInt
from flask import Blueprint, Flask, Request, jsonify, request
from url_check import URLValidator
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

atomic = AtomicInt()
app = Flask(__name__)
check = URLValidator()
# mapping = {}
auth_url = ""
mysql_url = ""

# use_db = False

db = SQLAlchemy()
mysql = MySQL(app)

class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False)

    def __int__(self, id, url):
        self.id = id
        self.url = url

def db_init():
    try:
        app.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
        db.init_app(app)
        with app.app_context():
            db.create_all()
    except Exception as e:
        print(e)
        exit(1)

def check_id(id:str):
    if not id.isnumeric():
        return jsonify({"Message": "Id should be numeric"}), 400

    id = int(id)
    num = Website.query.filter_by(id=id).count()
    if num < 1:
        return jsonify({"Message": "Not a valid id"}), 404

    return jsonify({"Message": "OK"}), 200

def retrieve_url(request:Request):
    body = request.get_json()
    if "url" not in body:
        return jsonify({"Message": "Wrong args"}), 400
    url = body["url"]

    msg, code = check(url)
    if code != 200:
        return msg, code

    return url, 200

def authenticate(request) -> bool:
    try:
        scheme, token = request.headers.get('Authorization').split(' ')
        if scheme != "Bearer":
            return False
        payload_b64 = token.split('.')[1]
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        if time.time() >= payload['exp']:
            return False
    except:
        return False

    r = requests.post(auth_url, json={"JWT":token})
    return r.status_code == 201

@app.before_first_request
def load_from_mysql():
    website = Website.query.all()
    gid = 0
    for o in website:
        gid = max(gid, o.id)
    atomic.val = gid + 1

@app.route('/<id>', methods = ["GET"])
def get_by_id(id:str):
    val, code = check_id(id)
    if code != 200:
        return val, code

    id = int(id)
    res = app.make_response("")
    cur_web = Website.query.get(id)
    res.headers["Location"] = cur_web.url
    res.status_code = 301
    return res

@app.route('/contains/<id>', methods = ["GET"])
def contains_id(id:str):
    if not id.isnumeric():
        return jsonify({"Message": "Id should be numeric"}), 400

    id = int(id)
    num = Website.query.filter_by(id=id).count()
    if num < 1:
        return "", 404
    else:
        return "", 200

@app.route('/<id>', methods = ["PUT"])
def put_by_id(id:str):
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    val, code = check_id(id)
    if code != 200:
        return val, code

    val, code = retrieve_url(request)
    if code != 200:
        return val, code

    id = int(id)
    website = Website.query.get(id)
    website.url = val
    db.session.commit()
    return jsonify({"Message": "Success"}), 200

@app.route('/<id>', methods = ["DELETE"])
def del_by_id(id:str):
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    val, code = check_id(id)
    if code != 200:
        return val, code

    id = int(id)
    website = Website.query.get(id)
    db.session.delete(website)
    db.session.commit()
    return "", 204

@app.route('/', methods = ["GET"])
def get_all_keys():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    website = Website.query.all()
    return json.dumps([o.id for o in website])

@app.route('/all', methods = ["GET"])
def get_all_mapping():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    website = Website.query.all()
    dic = {}
    for o in website:
        dic[o.id] = o.url
    return json.dumps(dic)

@app.route('/all', methods = ["DELETE"])
def del_all_mapping():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403

    website = Website.query.all()
    for o in website:
        db.session.delete(o)
    db.session.commit()
    return "", 204

@app.route('/', methods = ["POST"])
def post_url():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    val, code = retrieve_url(request)
    if code != 200:
        return val, code

    gid = atomic.get_and_inc()

    new_website = Website(id=gid, url=val)
    db.session.add(new_website)
    db.session.commit()
    res = app.make_response(json.dumps({'id':gid}))
    res.headers["Content-Type"] = "application/json"
    res.status_code = 201
    return res

@app.route('/', methods = ["DELETE"])
def delete():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    return jsonify({"Message": "Not Found"}), 404

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg.startswith('--db='):
                # use_db = True
                mysql_url = arg[5:]
                print("using mysql: " + mysql_url)
                db_init()
            if arg.startswith("--auth="):
                auth_url = arg[7:]

    if auth_url == "":
        print("Need to provide authentication service url.", file=sys.stderr)

    print("using authentication service: " + auth_url)

    app.run(
        host='0.0.0.0',
        port= 53333,
        debug=True
    )
