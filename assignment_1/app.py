from flask import Flask, request, Request, jsonify
import json
from atomic_int import AtomicInt
from url_check import URLValidator
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_mysqldb import MySQL

atomic = AtomicInt()
app = Flask(__name__)
check = URLValidator()
mapping = {}

db = SQLAlchemy()
ma = Marshmallow()
mysql = MySQL(app)

class Website(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(128), nullable=False)
    def __int__(self, id, url):
        self.id = id
        self.url = url

class WebsiteSchema(ma.Schema):
    class Meta:
        fields = ("id", "url")

website_schema = WebsiteSchema()
websites_schema = WebsiteSchema(many=True)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:123456@localhost/Website"
db.init_app(app)
with app.app_context():
    db.create_all()

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

    website = Website.query.get(id)
    db.session.delete(website)
    db.session.commit()
    return "", 204

@app.route('/', methods = ["GET"])
def get_all_keys():
    return json.dumps(list(mapping.keys()))

@app.route('/all', methods = ["GET"])
def get_all_mapping():
    data = Website.query.all()
    websites = websites_schema.dump(data)
    return jsonify(websites)
    # return json.dumps(mapping)

@app.route('/all', methods = ["DELETE"])
def del_all_mapping():
    mapping.clear()

    website = Website.query.all()
    db.session.delete(website)
    db.session.commit()
    return "", 204

@app.route('/', methods = ["POST"])
def post_url():
    val, code = retrieve_url(request)
    if code != 200:
        return val, code

    id = atomic.get_and_inc()
    mapping[id] = val

    new_website = Website(id, val)
    db.session.add(new_website)
    db.commit()
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