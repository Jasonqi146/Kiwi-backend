from flask import Flask, request
from flask_cors import CORS
import pymysql
import base64
import json

app = Flask(__name__)
CORS(app)
db = pymysql.connect(host="kiwidb.cyb2lfwpayeq.us-east-1.rds.amazonaws.com", user="KiwiAdm", passwd="KiwiPass0921")
cursor = db.cursor()
sql = "use dbo"
cursor.execute(sql)

@app.route("/")
def home():
  """get id based on product url"""
  product_url = request.args.get("product_url")
  sql = "Select id from item_data where path_name='{}'".format(product_url)
  cursor.execute(sql)
  response = cursor.fetchone()

  """fetch similiar product ids"""
  product_id = response[0]
  sql = "Select json from ranked_list where id={}".format(product_id)
  cursor.execute(sql)
  response = cursor.fetchone()
  same_product_ids = response[0]
  same_product_ids = json.loads(same_product_ids)
  same_product_ids = same_product_ids[:5]

  """if empty, calculate similarity score"""

  """get product info from AWS database"""
  product_info_list = []

  for product_id in same_product_ids:
    product_id = same_product_ids[0]
    sql = "Select * from item_data where id={}".format(product_id)
    cursor.execute(sql)
    product_info = cursor.fetchone()
    product = {
      "product_name": product_info[2],
      "website": product_info[3],
      "price": float(product_info[4]),
      "url": product_info[7]
    }
    sql = "Select image_bin from image_data where item_id={}".format(product_id)
    cursor.execute(sql)
    image_info = cursor.fetchone()
    image_info = image_info[0]
    product["image_stream"] = str(base64.b64encode(image_info))[2:-1]
    product_info_list.append(product)

  return json.dumps(product_info_list)

app.run()
