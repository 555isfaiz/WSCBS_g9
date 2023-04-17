from flask import Flask, Blueprint, request, Request, jsonify
import json
from atomic_int import AtomicInt
from url_check import URLValidator
import sys
from auth import authenticate

atomic = AtomicInt()
app = Flask(__name__)
# app.register_blueprint(auth_bp)
check = URLValidator()
mapping = {}
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


    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost/Website"
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
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
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
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
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
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
    # data = Website.query.all()
    # websites = websites_schema.dump(data)
    # return jsonify(websites)
    return json.dumps(mapping)

@app.route('/all', methods = ["DELETE"])
def del_all_mapping():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403

    mapping.clear()

    if use_db:
        website = Website.query.all()
        for o in website:
            db.session.delete(o)
        db.session.commit()
    return "", 204

@app.route('/', methods = ["POST"])
def post_url():
    if not authenticate(request):
        return jsonify({"Message": "forbidden"}), 403
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

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--db':
        use_db = True

    app.run(
        host='0.0.0.0',
        port= 53333,
        debug=True
    )