from flask import Flask, request, Response
import json
import random

app = Flask(__name__)
mapping = {}
counter = 0

@app.route('/<id>', methods = ["GET"])
def get_by_id(id):
    if id not in mapping:
        return "Not a valid id", 404
    
    return json.dumps("Location: {0}".format(mapping[id])), 301

@app.route('/<id>', methods = ["PUT"])
def put_by_id(id):
    mapping[id] = random.randint(0, 100)
    print(mapping)
    return "What should I do here..."

@app.route('/<id>', methods = ["DELETE"])
def del_by_id(id):
    if id not in mapping:
        return "Not a valid id", 404
    
    mapping.pop(id)
    return 204

@app.route('/', methods = ["GET"])
def get_all_keys():
    return json.dumps(list(mapping.keys()))

@app.route('/', methods = ["POST"])
def post_url(url):
    global counter
    if url not in request.args:
        return "Wrong args", 400
    
    url = request.args.get("url")

    # validate the url...

    id = counter
    counter = id + 1
    mapping[id] = url
    return str(id), 201

@app.route('/', methods = ["DELETE"])
def delete():
    return "Not Found", 404

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port= 53333,
        debug=True
    )