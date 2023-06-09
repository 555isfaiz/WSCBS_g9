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
users = {}

use_db = False

try:
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


    auth.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root@localhost/User"
    db.init_app(auth)
    with auth.app_context():
        db.create_all()
except Exception as e:
    print(e)
    print("Run without DB.")

@auth.before_first_request
def load_from_mysql():
    if use_db:
        uu = User.query.all()
        for o in uu:
            users[o.username] = o.password
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
        if time.time() < exp and iat > users[username][1] and hmac.compare_digest(signature_b64, expected_signature_b64):
            return jsonify({"Username": username}), 201
        return jsonify({"Message": "forbidden"}), 403
    except:
        return jsonify({"Message": "forbidden"}), 403

@auth.route('/users', methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")
    cur_time = time.time()

    if username not in users:
        hash_password = generate_password_hash(password=password)
        users[username] = (hash_password, cur_time)
        if use_db:
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

    if check_password_hash(users[username][0], old_password):
        hash_password = generate_password_hash(password=new_password)
        users[username] = (hash_password, cur_time)
        if use_db:
            user = User.query.get(username)
            user.password = hash_password
            user.start_time = cur_time
            db.session.commit()
        return jsonify({"Message": "success"}), 200
    else:
        return jsonify({"Message": "forbidden"}), 403

@auth.route('/users/login', methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if username in users and check_password_hash(users[username][0], password):
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
    else:
        return jsonify({"Message": "forbidden"}), 403

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--db':
        use_db = True

    auth.run(
        host='0.0.0.0',
        port= 60000,
        debug=True
    )
