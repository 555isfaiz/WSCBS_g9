from url import value_gen
import requests

def test_api():
    unqiue_val = value_gen()
    url = "http://127.0.0.1:5000/"
    r = requests.post(url, json={'url': unqiue_val})
    print(r.text)

test_api()