from urllib.request import urlopen, Request
import urllib.error
import base64
import json
from pprint import pprint


def user_authenticator():
  """A function in the client side to check authenticate itself with the username and password and then
    getting a bearer token"""

  username = "user"
  password = "pass"
  credentials = f"{username}:{password}"
  encoded_cred = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
  header = {"Authorization": f"Basic {encoded_cred}"}
  login_url = "http://127.0.0.1:5000/user"
  login_request = Request(url=login_url, headers=header)
  try:
    with urlopen(login_request) as login_response:
      dict_token = json.loads(login_response.read())
      token = dict_token["token"]
      return token
  except urllib.error.HTTPError as error:
    print(error.reason)


#creating authorization header and assigning the bearer token
token = user_authenticator()
header = {"Authorization": token}


def print_products():
  """A function to send a get request to the flask API"""

  try:
    #Hitting the get request and then displaying all products,and accessing one product from them
    get_url = "http://127.0.0.1:5000/products/get"
    get_request = Request(url=get_url, method="GET", headers=header)

    with urlopen(url=get_request) as get_response:
      get_body = get_response.read()
      all_products = json.loads(get_body)
      print("All available products :")
      pprint(all_products)

  except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"), error.reason)


def print_product(product_name="iPhone"):
  """A function to send a get request to the flask API"""

  try:
    # Hitting the getting particular product request and then displaying product

    get_product_url = f"http://127.0.0.1:5000/products/get/{product_name}"
    get_product_request = Request(url=get_product_url,
                                  method="GET",
                                  headers=header)
    with urlopen(url=get_product_request) as get_product_response:
      get_product_body = get_product_response.read()
      print(f"Details of product :{product_name} ")
      print(json.loads(get_product_body))
  except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"), error.reason)


def add_product(product={
  "Product_Name": "Nokia",
  "Product_Price": 70000,
  "Description": "8GB|126GB"
}):
  """A function to send a post request to the flask API"""

  try:
    data = json.dumps(product).encode("utf-8")

    add_product_url = "http://127.0.0.1:5000/products/add"
    add_product_request = Request(url=add_product_url,
                                  method="POST",
                                  headers=header,
                                  data=data)
    # Hitting the add product request and then displaying the response
    with urlopen(url=add_product_request) as add_product_response:
      add_product_body = add_product_response.read()
      print(json.loads(add_product_body))
    print_products()

  except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"), error.reason)


def update_product(product_name="Nokia"):
  """A function to send a put request to the flask API"""

  try:
    details = {"Product_Price": 80000, "Description": "8GB|256GB"}
    data = json.dumps(details).encode("utf-8")

    update_product_ulr = f"http://127.0.0.1:5000/products/update/{product_name}"
    update_product_request = Request(url=update_product_ulr,
                                     method="PUT",
                                     headers=header,
                                     data=data)
    # Hitting the update particular product request and then displaying response message
    with urlopen(url=update_product_request) as update_product_response:
      update_product_body = update_product_response.read()
      print(json.loads(update_product_body))
    print("Updated data :")
    print_product(product_name)
  except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"), error.reason)


def del_product(product_name="Nokia"):
  """A function to send a delete request to the flask API"""

  try:
    del_product_ulr = f"http://127.0.0.1:5000/products/delete/{product_name}"
    del_product_request = Request(url=del_product_ulr,
                                  method="DELETE",
                                  headers=header)
    # Hitting the delete particular product request and then displaying response message
    with urlopen(url=del_product_request) as del_product_response:
      del_product_body = del_product_response.read()
      print(json.loads(del_product_body))
    print("Available products after deleting :")
    print_products()
  except urllib.error.HTTPError as error:
    print(error.read().decode("utf-8"), error.reason)


print_products()
print()
print_product()
print()
add_product()
print()
update_product()
print()
del_product()
