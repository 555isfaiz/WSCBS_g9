from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import requests
app = Flask(__name__)

limiter = Limiter(
    app,
    default_limits=["100 per minute"]
)


# Auth Microservice
@app.route('/auth_microservice/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit("10 per minute")
def serve_authmicroservice(path):
    url = 'http://127.0.0.1:60000/' + path
    # headers = {'Content-Type': 'application/json'}
    response = requests.request(request.method, url, headers=request.headers, json=request.json)
    return jsonify(response.json()), response.status_code

# App Microservice
@app.route('/app_microservice', defaults={'path': '/'}, methods=['GET', 'POST', 'PUT', 'DELETE'])
@app.route('/app_microservice/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
@limiter.limit("20 per minute")
def serve_appmicroservice(path):
    url = 'http://127.0.0.1:53333/' + path
    #headers = {'Content-Type': 'application/json'}
    if request.method == "POST" or request.method == "PUT":
        response = requests.request(request.method, url, headers=request.headers, json=request.get_json())
    else:
        response = requests.request(request.method, url, headers=request.headers, allow_redirects=False)
    try:
        res = response.json()
    except:
        res = response.text
    resp = app.make_response(res)
    resp.status_code = response.status_code
    for k in response.headers:
        resp.headers[k] = response.headers[k]
    return resp

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=53334)
