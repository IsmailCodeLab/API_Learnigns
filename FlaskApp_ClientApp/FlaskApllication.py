import datetime
import re
import json
from functools import wraps

import jwt
from flask import Flask, request, jsonify
import sqlite3

# HTTP Error Codes (200, 400, 404, 500)
# 200:The request succeeded.It tells the request has been processed successfully
# 201:The request succeeded, and a new resource was created as a result.
#     This is typically the response sent after POST requests, or some PUT requests.
# 400:Bad Request(Invalid and missing request parameters,unsupported request methods)
# 401:Unauthorized.The client must authenticate itself to get the requested response.
# 404:Resource Not Found(when the resource not found on the server side,Invalid urls)
# 500:Internal server error. while processing the request an exception occurred in the code.

app = Flask(__name__)

app.config['SECRET_KEY'] = '1234asdfg!@#$'


def token_validator(original_func):
  """A decorator function to take bearer token from the post-man  and validates them
         and then executes the decorated function."""

  @wraps(original_func)
  def decorated(*args, **kwargs):
    bearer = request.headers.get('Authorization', None)
    if bearer is None:
      return jsonify({"error": "Please enter your bearer token"}), 400
    try:
      token = bearer.split()[1]
      decoded_token = jwt.decode(token,
                                 app.config['SECRET_KEY'],
                                 algorithms=["HS256"])
      return original_func(*args, **kwargs)
    except IndexError:
      return jsonify({'message': 'Invalid bearer token'}), 401
    except jwt.exceptions.DecodeError:
      return jsonify({'message': 'Invalid bearer token'}), 401
    except jwt.exceptions.ExpiredSignatureError:
      return jsonify(
        {'message': 'Your session has expired.Please login again'}), 401

  return decorated


@app.route("/user", methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_login():
  """A function to take username and password from the user and validates them
        and then generates a bearer token for the user that can used later for validation purpose"""

  if request.method == 'GET':
    user = request.authorization
    if not user:
      return jsonify({"error": "Enter user credentials"})
    elif (user.username == 'user' and user.password == 'pass'):
      token = jwt.encode(
        {
          'user': user.username,
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, app.config['SECRET_KEY'])
      return jsonify({'token': "Bearer " + token}), 200
    else:
      return jsonify({"error": "Invalid user credentials"}), 401
  else:
    return jsonify({"error": "Method  not allowed"}), 400


def get_database_connection():
  """This function connects with the database and returns the connection"""

  connection = sqlite3.connect('database.db')
  return connection


connection = get_database_connection()
connection.execute(
  'CREATE TABLE IF NOT EXISTS products (Product_Name text not null unique,Product_Price integer not null,\
    Description text not null)')


@app.route("/products/get/<string:product_name>", methods=['GET'])
@app.route("/products/get", methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_validator
def get_products(product_name=None):
  """This function returns the list of all products available in the database."""

  # To get connection with the data base
  try:
    connect = get_database_connection()
  except sqlite3.Error as error:
    return jsonify({"error": str(error)})
  cursor = connect.cursor()
  try:

    if request.method == 'GET':
      try:
        data = request.get_json()
        if data is not None:
          return jsonify(
            {"error":
             "More than required inputs given.(No need of inputs)"}), 400

        # To check user given product name in URL or not
        if product_name:
          # To check given product name is valid or not
          if not re.search('^[A-Za-z]+', product_name):
            return jsonify({
              "error":
              "Product name you entered in URL is invalid.It should start with alphabet"
            }), 400
          query = "select * from products where Product_Name=(?)"
          result = cursor.execute(query, (product_name, ))
        else:
          query = "select * from products"
          result = cursor.execute(query)
      except sqlite3.OperationalError:
        return jsonify(
          {"error": "Sorry,products table doesn't exist in database"}), 500
      except sqlite3.Error as error:
        return jsonify({"error": str(error)})
      products = result.fetchall()
      connect.close()

      # To check  weather we have products or not
      if len(products) > 0:
        coloumns = ['Product_Name', 'Product_Price', 'Description']
        dictionary = [{key: value
                       for key, value in zip(coloumns, row)}
                      for row in products]
        return jsonify(dictionary), 200
      else:
        if product_name:
          return jsonify(
            {"Message": f"No product found with name '{product_name}'"}), 404
        else:
          return jsonify({"Message": "No products in the database"}), 200
    else:
      return jsonify({"error": "Method not allowed"}), 400
  except Exception as error:
    return jsonify({"error": error}), 500


@app.route("/products/add", methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_validator
def add_product():
  """This function adds  the product that was given by the user to the database
       when the given method type is POST. If the product already exist in the database returns an error message"""

  # To get connection with the data base
  try:
    connect = get_database_connection()
  except sqlite3.Error as error:
    return jsonify({"error": str(error)})
  cursor = connect.cursor()
  if request.method == 'POST':

    try:
      # To take json input from the user
      data = json.loads(request.get_data())
      # To validate the number of parameters given by user
      if data is None:
        return jsonify({"error": "Provide inputs"}), 400
      elif len(data) < 3:
        return jsonify({"error": "Inputs are not sufficient"}), 400
      elif len(data) > 3:
        return jsonify({"error": "More inputs than required are given"}), 400

      product_name = data['Product_Name']
      product_price = data['Product_Price']
      description = data['Description']

      # To validate the parameters given by user
      if not isinstance(product_price, int):
        return jsonify({"error": "Product price should be integer value"}), 400
      elif product_price < 0:
        return jsonify({"error": "Product price cannot be negative"}), 400
      elif not re.search('^[A-Za-z]+', product_name):
        return jsonify({"error":
                        "Product_Name should start with alphabets"}), 400
      elif not re.search('[A-Za-z]+', description):
        return jsonify({"error": "Description should contain alphabets"}), 400
    except KeyError:
      return jsonify({
        "error":
        "Invalid keys in inputs (Please check FlaskApplication_Inputs.txt \
                                      to know how to give inputs)"
      }), 400
    try:
      query = "insert into products (Product_Name,Product_Price,Description) values (?,?,?)"
      cursor.execute(query, (product_name, product_price, description))
    except sqlite3.IntegrityError:
      return jsonify({"error": "Product with that name already exist"}), 400
    except sqlite3.OperationalError:
      return jsonify(
        {"error": "Sorry,products table doesn't exist in database"}), 500
    except sqlite3.Error as error:
      return jsonify({"error": str(error)}), 500
    connect.commit()
    connect.close()
    return jsonify({"message":
                    f"Successfully product '{product_name}' added"}), 201
  else:
    return jsonify({"error": "Method not allowed"}), 400


@app.route("/products/update/<string:product_name>",
           methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_validator
def update_product(product_name=None):
  """This function updates the Product_Price and Description based on the product entered
        in the URL and when the method type is PUT.It takes Product_Price and Description as input
        from the user in JSON format"""

  # To get connection with the data base
  try:
    connect = get_database_connection()
  except sqlite3.Error as error:
    return jsonify({"error": str(error)})
  cursor = connect.cursor()
  if request.method == 'PUT':

    try:

      # To validate the input given by user
      if not re.search('^[A-Za-z]+', product_name):
        return jsonify({
          "error":
          "Product name you entered in URL is invalid.It should start with alphabet"
        }), 400

      data = json.loads(request.get_data())

      # To validate the number of parameters given by user
      if data is None:
        return jsonify({"error": "Please provide inputs"}), 400
      elif len(data) < 2:
        return jsonify({"error": "Inputs are not sufficient"}), 400
      elif len(data) > 2:
        return jsonify({"error": "More inputs than required are given"}), 400
      product_price = data['Product_Price']
      description = data['Description']

      # To validate the parameters given by user
      if not isinstance(product_price, int):
        return jsonify({"error": "Product price should be integer value"}), 400
      elif product_price < 0:
        return jsonify({"error": "Product price cannot be negative"}), 400
      elif not re.search('[A-Za-z]+', description):
        return jsonify({"error": "Description should contain alphabets"}), 400

    except KeyError:
      return jsonify({
        "error":
        "Invalid keys in inputs (Please check FlaskApplication_Inputs.txt \
                              to know how to give inputs)"
      }), 500
    try:
      query = "update products set Product_Price=(?),Description=(?) where Product_Name=(?)"
      result = cursor.execute(query,
                              (product_price, description, product_name))
    except sqlite3.OperationalError:
      return jsonify(
        {"error": "Sorry,products table doesn't exist in database"}), 500
    except sqlite3.Error as error:
      return jsonify({"error": str(error)}), 500
    connect.commit()
    connect.close()

    #To find weather we updated the data or not
    if result.rowcount > 0:
      return jsonify(
        {"message":
         f"Successfully product  '{product_name}' data updated"}), 200
    else:
      return jsonify(
        {"message": f"Product with name '{product_name}' not found"}), 404
  else:
    return jsonify({"error": "Method not allowed"}), 400


@app.route('/products/delete/<string:product_name>',
           methods=['GET', 'POST', 'PUT', 'DELETE'])
@token_validator
def delete_product(product_name=None):
  # To get connection with the database
  try:
    connect = get_database_connection()
  except sqlite3.Error as error:
    return jsonify({"error": str(error)})
  cursor = connect.cursor()
  if request.method == 'DELETE':
    """This if-condition deletes the particular product based on the product name entered in URL
        and when the method type is DELETE."""

    data = request.get_json()

    # To validate the number of parameters given by user
    if data is not None:
      return jsonify(
        {"error":
         "More than required inputs are given.(No need of inputs)"}), 400

    # To check weather user given product name or not in url
    if product_name:
      # To validate the input given by user
      if not re.search('^[A-Za-z]+', product_name):
        return jsonify({
          "error":
          "Product name you entered in URL is invalid.It should start with alphabet"
        }), 400
    else:
      return jsonify({"error": "Method not allowed"}), 400

    try:
      query = "delete from products where Product_Name=(?)"
      result = cursor.execute(query, (product_name, ))
    except sqlite3.OperationalError:
      return jsonify(
        {"error": "Sorry,products table doesn't exist in database"}), 500
    except sqlite3.Error as error:
      return jsonify({"error": str(error)}), 500
    connect.commit()
    connect.close()

    #To check weather we delete the product or not
    if result.rowcount > 0:
      return jsonify({
        "message":
        f"Product with name '{product_name}' deleted successfully"
      }), 200
    else:
      return jsonify(
        {"message": f"Product with name '{product_name}' not found"}), 404
  else:
    return jsonify({"error": "Method not allowed"}), 400


@app.route("/products/filter", methods=['GET', 'POST', 'DELETE', 'PUT'])
@token_validator
def filter_products():
  """This function is to get list of products that are ordered by price and they are in the given price range.
    Returns product not found error if no product with in that range
    This function takes two inputs start_price and end_price"""

  #To get connection with database
  try:
    connect = get_database_connection()
  except sqlite3.Error as error:
    return jsonify({"error": str(error)})
  cursor = connect.cursor()
  try:
    if request.method == 'GET':
      data = json.loads(request.get_data())
      try:
        if data is None:
          return jsonify({"error": "Please provide inputs"}), 400
        elif len(data) < 2:
          return jsonify({"error": "Inputs are not sufficient"}), 400
        elif len(data) > 2:
          return jsonify({"error": "More inputs than required are given"}), 400
        start_price = data['Start_Price']
        end_price = data['End_Price']
        if not (isinstance(start_price, int) and isinstance(end_price, int)):
          return jsonify({"error":
                          "Product price should be integer value"}), 400
        elif start_price < 0 or end_price < 0:
          return jsonify({"error":
                          "Product price range cannot be negative"}), 400
        elif start_price > end_price:
          return jsonify({"error": "Provide an valid price range"}), 400
      except KeyError:
        return jsonify({
          "error":
          "Invalid keys in inputs (Please check FlaskApplication_Inputs.txt \
                                              to know how to give inputs)"
        }), 400
      try:
        query = "select * from products where Product_Price between (?) and (?) order by Product_Price"
        result = cursor.execute(query, (start_price, end_price))
      except sqlite3.OperationalError:
        return jsonify({{
          "error":
          "Sorry,products table doesn't exist in database"
        }}), 500
      except sqlite3.Error as error:
        return jsonify({"error": str(error)}), 500
      products = result.fetchall()
      connect.close()
      #To check weather we have any products in the specified range
      if len(data) > 0:
        coloumns = ['Product_Name', 'Product_Price', 'Description']
        dictionary = [{key: value
                       for key, value in zip(coloumns, row)}
                      for row in products]
        return jsonify(dictionary), 200
      else:
        return jsonify({
          "Message":
          f"Products with in the price range of '{start_price}' and '{end_price}' not found"
        }), 400
    else:
      return jsonify({"error": "Method not allowed"}), 400
  except:
    return jsonify({"error": "Some internal server error"}), 500


@app.errorhandler(404)
def Invalid_url_handler(error):
  """To handle the invalid urls entered by the user"""

  return jsonify({"error": "Invalid url"}), 404


if __name__ == '__main__':
  app.run(debug=True)
