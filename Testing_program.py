import requests
import json,jsonpath

def test_add_post():
    with open("data.json","r") as file:
        data=json.load(file)
    url="https://reqres.in/api/users"
    response=requests.post(url,data)
    print(response.text)