import requests
import json
from jsonpath import jsonpath
url="https://reqres.in/api/users"

res=requests.get(url)
print(res.status_code)
json_data=json.loads(res.text)
# id=json_data['data']['id']
print(json_data)
pages=jsonpath(json_data,'total_pages')
print(pages)
assert pages[0]==2