import json
import sys

from atomic_int import AtomicInt
from flask import Flask
from flask_mysqldb import MySQL
from flask_sqlalchemy import SQLAlchemy

atomic = AtomicInt()
app = Flask(__name__)
mysql_url = ""

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

@app.before_first_request
def load_from_mysql():
    website = Website.query.all()
    gid = 0
    for o in website:
        gid = max(gid, o.id)
    atomic.val = gid + 1

@app.route('/', methods = ["GET"])
def gen_id():
    gid = atomic.get_and_inc()
    return json.dumps({'id':gid})

if __name__ == '__main__':
    if len(sys.argv) > 1:
        for arg in sys.argv:
            if arg.startswith('--db='):
                mysql_url = arg[5:]
                print("using mysql: " + mysql_url)
                db_init()

    app.run(
        host='0.0.0.0',
        port= 55555,
        debug=True
    )
