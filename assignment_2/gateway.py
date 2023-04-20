from flask import Flask, request, jsonify
import requests
app = Flask(__name__)

# Auth Microservice
@app.route('/auth_microservice/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def serve_authmicroservice(path):
    url = 'http://127.0.0.1:60000/' + path
    headers = {'Content-Type': 'application/json'}
    response = requests.request(request.method, url, headers=headers, json=request.json)
    return jsonify(response.json()), response.status_code

# App Microservice
@app.route('/app_microservice/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def serve_appmicroservice(path):
    url = 'http://127.0.0.1:53333/'
    headers = {'Content-Type': 'application/json'}
    response = requests.request(request.method, url, headers=headers, json=request.json)
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=53334)
