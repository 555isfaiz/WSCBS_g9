from flask import Flask, request, Request
import json
import random
from atomic_int import AtomicInt
import sys

use_db = False
atomic = AtomicInt()
app = Flask(__name__)
mapping = {}

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

    # validate the url...

    return url, 200

@app.route('/<id>', methods = ["GET"])
def get_by_id(id:str):
    val, code = check_id(id)
    if code != 200:
        return val, code

    id = int(id)
    # TODO change response header here
    return json.dumps({"Location": "{0}".format(mapping[id])}), 301

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
    return "Success", 200

@app.route('/<id>', methods = ["DELETE"])
def del_by_id(id:str):
    val, code = check_id(id)
    if code != 200:
        return val, code

    id = int(id)
    mapping.pop(id)
    return "", 204

@app.route('/', methods = ["GET"])
def get_all_keys():
    return json.dumps(list(mapping.keys()))

@app.route('/all', methods = ["GET"])
def get_all_mapping():
    return json.dumps(mapping)

@app.route('/all', methods = ["DELETE"])
def del_all_mapping():
    mapping.clear()
    return "", 204

@app.route('/', methods = ["POST"])
def post_url():
    val, code = retrieve_url(request)
    if code != 200:
        return val, code

    id = atomic.get_and_inc()
    mapping[id] = val

    return str(id), 201

@app.route('/', methods = ["DELETE"])
def delete():
    return "Not Found", 404

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--db':
        use_db = True

    app.run(
        host='0.0.0.0',
        port= 53333,
        debug=True
    )