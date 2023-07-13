import requests
import json

#Authenticate the user
login_url = "http://127.0.0.1:5000/user"
token_response = requests.get(login_url, auth=("user", "pass"))
token = token_response.json()["token"]

#Storing the token in the authorization header to authenticate in the api
header = {"Authorization": token}


def test_get_products_api():
  """Test script for the api that give all products"""

  products_url = "http://127.0.0.1:5000/products/get"
  all_products = requests.get(products_url, headers=header)
  assert all_products.status_code == 200
  pretty_json = json.dumps(all_products.text, indent=4)
  print("\nAll products\n", json.loads(pretty_json))


def test_get_product_api():
  """Test script for the api that gives particular product"""
  product_name = "iPhone"
  product_url = "http://127.0.0.1:5000/products/get/" + product_name
  product = requests.get(product_url, headers=header)
  assert product.status_code == 200
  pretty_json = json.dumps(product.text, indent=4)
  print("\nProduct :\n", json.loads(pretty_json))


def test_post_product_api():
  """Test script for the api that creates a product"""
  product_name = "Realme11"
  create_product_url = "http://127.0.0.1:5000/products/add"
  product = {
    "Product_Name": product_name,
    "Product_Price": 12000,
    "Description": "6GB|64GB"
  }
  response = requests.post(create_product_url, json=product, headers=header)

  assert response.status_code == 201, f"{response.text}"
  prety_json = json.dumps(response.text, indent=4)
  print("\nMessage :\n", prety_json)


def test_update_product_api():
  """Test script to test the update product api"""

  product_name = "Realme11"
  product_data = {"Product_Price": 12000, "Description": "4GB|64GB"}
  update_product_url = "http://127.0.0.1:5000/products/update/" + product_name

  response = requests.put(url=update_product_url,
                          json=product_data,
                          headers=header)

  assert response.status_code == 200, response.text

  prety_json = json.dumps(response.text, indent=4)
  print("\nMessage :\n", prety_json)


def test_delete_product_api():
  """Test script for testing the delete api"""
  product_name = "Realme11"
  delete_product_url = "http://127.0.0.1:5000/products/delete/" + product_name

  response = requests.delete(url=delete_product_url, headers=header)
  assert response.status_code == 200, f"{response.text}"

  prety_json = json.dumps(response.text, indent=4)
  print("\nMessage :\n", prety_json)
