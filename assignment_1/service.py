from url import value_gen
from app import *

def test_api():
    url = value_gen()
    post_url(url)
    return ("service succesfully tested")

test_api()