from flask import Flask, Blueprint, request, Request, jsonify
import json
import hashlib
import hmac
import base64
import time
import sys
from werkzeug.security import generate_password_hash, check_password_hash

auth = Flask(__name__)
auth.config["SECRET_KEY"] = "123456"
mysql_url = ""

from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
db = SQLAlchemy()
mysql = MySQL(auth)

class User(db.Model):
    username = db.Column(db.String(256), primary_key=True)
    password = db.Column(db.String(256), nullable=False)
    start_time = db.Column(db.Integer, nullable=False)

    def __int__(self, _username, _password):
        self.username = _username
        self.password = _password

def db_init():
    try:
        auth.config["SQLALCHEMY_DATABASE_URI"] = mysql_url
        db.init_app(auth)
        with auth.app_context():
            db.create_all()
    except Exception as e:
        print(e)
        print("Run without DB.")


# @auth.before_first_request
# def load_from_mysql():
#     if use_db:
#         uu = User.query.all()
#         for o in uu:
#             users[o.username] = (o.password, o.start_time)

@auth.route('/authenticate', methods=["POST"])
def authenticate():
    token = request.json.get("JWT")
    try:
        header_b64, payload_b64, signature_b64 = token.split('.')
        payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode())
        username = payload["sub"]
        exp = payload["exp"]
        iat = payload["iat"]
        message = header_b64 + '.' + payload_b64
        expected_signature = hmac.new(auth.config["SECRET_KEY"].encode(), message.encode(), hashlib.sha256)
        expected_signature_b64 = base64.urlsafe_b64encode(expected_signature.digest()).decode()
        cur_user = User.query.get(username)
        cur_time = cur_user.start_time
        if time.time() < exp and iat > cur_time and hmac.compare_digest(signature_b64, expected_signature_b64):
            return jsonify({"Username": username}), 201
        return jsonify({"Message": "forbidden"}), 403
    except:
        return jsonify({"Message": "forbidden"}), 403

@auth.route('/users', methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")
    cur_time = time.time()

    num = User.query.filter_by(username=username).count()
    if num < 1:
        hash_password = generate_password_hash(password=password)
        new_user = User(username=username, password=hash_password, start_time=cur_time)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"Message": "success"}), 201
    else:
        return jsonify({"Message": "duplicate"}), 409

@auth.route('/users', methods=["PUT"])
def change_password():
    username = request.json.get("username")
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    cur_time = time.time()

    cur_user = User.query.get(username)
    cur_password = cur_user.password
    if check_password_hash(cur_password, old_password):
        hash_password = generate_password_hash(password=new_password)
        cur_user.password = hash_password
        cur_user.start_time = cur_time
        db.session.commit()
        return jsonify({"Message": "success"}), 200
    else:
        return jsonify({"Message": "forbidden"}), 403

@auth.route('/users/login', methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    try:
        cur_user = User.query.get(username)
        if cur_user and check_password_hash(cur_user.password, password):
            # Generate authentication token
            header = {
                "alg": "HS256",
                "typ": "JWT"
            }
            payload = {
                "iss": "group_9",
                "sub": username,
                "aud": "url_shortener_application",
                "nbf": int(time.time()),
                "iat": int(time.time()),
                "exp": int(time.time() + 300)
            }
            header_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).decode()
            payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
            message = header_b64 + '.' + payload_b64
            signature = hmac.new(auth.config["SECRET_KEY"].encode(), message.encode(), hashlib.sha256)
            signature_b64 = base64.urlsafe_b64encode(signature.digest()).decode()
            token = message + '.' + signature_b64
            return jsonify({"JWT": token}), 200
    except Exception as exp:
        return jsonify({"Message": "forbidden"}), 403

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg.startswith('--db='):
                mysql_url = arg[5:]
                print("using mysql: " + mysql_url)
                db_init()

    auth.run(
        host='0.0.0.0',
        port=60000,
        debug=True
    )
