import requests,json,jsonpath
url="https://reqres.in/api/users"

file=open("data.json","r")
data=json.load(file)
file.close()
print(data,type(data))

response=requests.post(url,data)
id=jsonpath.jsonpath(json.loads(response.text),'id')
print(id[0],type(id[0]))