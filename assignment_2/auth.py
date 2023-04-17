from flask import Flask, Blueprint, request, Request, jsonify
import json
import hashlib
import hmac
import base64
import time

auth_bp = Blueprint("auth", __name__)
SECRET_KEY = "123456"
users = {}

def authenticate(request:Request):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return False
    token = auth_header.split(' ')[1]
    print(token)
    try:
        decoded_token = base64.b64decode(token.encode())
        message, signature = decoded_token[:-32], decoded_token[-32:]
        expected_signature = hmac.new(SECRET_KEY.encode(), message, hashlib.sha256).digest()
        if hmac.compare_digest(signature, expected_signature):
            return True
        return False
    except:
        return False

@auth_bp.route('/users', methods=["POST"])
def register():
    username = request.json.get("username")
    password = request.json.get("password")

    if username not in users:
        users[username] = password
        return jsonify({"Message": "success"}), 201
    else:
        return jsonify({"Message": "duplicate"}), 409

@auth_bp.route('/users', methods=["PUT"])
def change_password():
    username = request.json.get("username")
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")

    if old_password == users[username]:
        users[username] = new_password
        return jsonify({"Message": "success"}), 200
    else:
        return jsonify({"Message": "forbidden"}), 403

@auth_bp.route('/users/login', methods=["POST"])
def login():
    username = request.json.get("username")
    password = request.json.get("password")

    if username in users and users[username] == password:
        # Generate authentication token
        timestamp = str(int(time.time()))
        message = username + ':' + timestamp
        signature = hmac.new(SECRET_KEY.encode(), message.encode(), hashlib.sha256).digest()
        token = base64.b64encode(message.encode() + signature).decode("utf-8")
        return jsonify({"JWT": token}), 200
    else:
        return jsonify({"Message": "forbidden"}), 403