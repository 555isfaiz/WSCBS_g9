from flask import Flask, request, Request, jsonify
import json
import hashlib
import hmac
import base64
import time
from atomic_int import AtomicInt
from url_check import URLValidator
import sys


atomic = AtomicInt()
app = Flask(__name__)
app.config["SECRET_KEY"] = "123456"
check = URLValidator()
mapping = {}
users = {}
gid = 0

use_db = False

try:
    from flask_sqlalchemy import SQLAlchemy
    from flask_mysqldb import MySQL
    db = SQLAlchemy()
    mysql = MySQL(app)

    class Website(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        url = db.Column(db.String(128), nullable=False)

        def __int__(self, id, url):
            self.id = id
            self.url = url


    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/Website"
    db.init_app(app)
    with app.app_context():
        db.create_all()
except Exception as e:
    print(e)
    print("Run without DB.")

def check_id(id:str):
    if not id.isnumeric():
        return "Id should be numeric", 400

    id = int(id)
    if id not in mapping:
        return "Not a valid id", 404

    return "OK", 200

def retrieve_url(request:Request):
    body = request.get_json()
    if "url" not in body:
        return "Wrong args", 400
    url = body["url"]

    msg, code = check(url)
    if code != 200:
        return msg, code

    return url, 200

def authenticate(request:Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    token = auth_header.split(' ')[1]
    print(token)
    try:
        decoded_token = base64.b64decode(token.encode())
        message, signature = decoded_token[:-32], decoded_token[-32:]
        expected_signature = hmac.new(app.config['SECRET_KEY'].encode(), message, hashlib.sha256).digest()
        if hmac.compare_digest(signature, expected_signature):
            return True
        return False
    except:
        return False

@app.before_first_request
def load_from_mysql():
    global gid
    if use_db:
        website = Website.query.all()
        for o in website:
            mapping[o.id] = o.url
            gid = max(gid, o.id)
        atomic.val = gid + 1

@app.route('/<id>', methods = ["GET"])
def get_by_id(id:str):
    val, code = check_id(id)
    if code != 200:
        return val, code

    id = int(id)
    res = app.make_response("")
    res.headers["Location"] = mapping[id]
    res.status_code = 301
    return res

@app.route('/contains/<id>', methods = ["GET"])
def contains_id(id:str):
    if not id.isnumeric():
        return "Id should be numeric", 400

    id = int(id)
    if id not in mapping:
        return "", 404
    else:
        return "", 200

@app.route('/<id>', methods = ["PUT"])
def put_by_id(id:str):
    val, code = check_id(id)
    if code != 200:
        return val, code

    val, code = retrieve_url(request)
    if code != 200:
        return val, code

    id = int(id)
    mapping[id] = val

    if use_db:
        website = Website.query.get(id)
        website.url = val
        db.session.commit()
    return "Success", 200

@app.route('/<id>', methods = ["DELETE"])
def del_by_id(id:str):
    val, code = check_id(id)
    if code != 200:
        return val, code

    id = int(id)
    mapping.pop(id)

    if use_db:
        website = Website.query.get(id)
        db.session.delete(website)
        db.session.commit()
    return "", 204

@app.route('/', methods = ["GET"])
def get_all_keys():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    return json.dumps(list(mapping.keys()))

@app.route('/all', methods = ["GET"])
def get_all_mapping():
    # data = Website.query.all()
    # websites = websites_schema.dump(data)
    # return jsonify(websites)
    return json.dumps(mapping)

@app.route('/all', methods = ["DELETE"])
def del_all_mapping():
    mapping.clear()

    if use_db:
        website = Website.query.all()
        for o in website:
            db.session.delete(o)
        db.session.commit()
    return "", 204

@app.route('/', methods = ["POST"])
def post_url():
    global gid
    val, code = retrieve_url(request)
    if code != 200:
        return val, code

    gid = atomic.get_and_inc()
    mapping[gid] = val

    if use_db:
        new_website = Website(id=gid, url=val)
        db.session.add(new_website)
        db.session.commit()
    res = app.make_response(json.dumps({'id':gid}))
    res.headers["Content-Type"] = "application/json"
    res.status_code = 201
    return res

@app.route('/', methods = ["DELETE"])
def delete():
    return "Not Found", 404

@app.route('/users', methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")

    if username not in users:
        users[username] = password
        return jsonify({"Message": "success"}), 201
    else:
        return jsonify({"Message": "duplicate"}), 409

@app.route('/users', methods=["PUT"])
def change_password():
    username = request.json.get("username")
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if old_password == users[username]:
        users[username] = new_password
        return jsonify({"Message": "success"}), 200
    else:
        return jsonify({"Message": "forbidden"}), 403

@app.route('/users/login', methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if username in users and users[username] == password:
        # Generate authentication token
        timestamp = str(int(time.time()))
        message = username + ':' + timestamp
        signature = hmac.new(app.config["SECRET_KEY"].encode(), message.encode(), hashlib.sha256).digest()
        token = base64.b64encode(message.encode() + signature).decode("utf-8")
        return jsonify({"JWT": token}), 200
    else:
        return jsonify({"Message": "forbidden"}), 403


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--db':
        use_db = True

    app.run(
        host='0.0.0.0',
        port= 53333,
        debug=True
    )
