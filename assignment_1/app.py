from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    pass

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port= 53333,
        debug=True
    )