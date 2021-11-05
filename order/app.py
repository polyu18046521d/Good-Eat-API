from flask import Flask, abort, jsonify, request
import db

app = Flask(__name__)

@app.route("/<order_id>", methods=["GET"])
def get_order(order_id):
  res = list(db.access_order().find({"order_id": order_id}, {"_id": 0}))
  return response_helper(200, res)

def response_helper(status, json_val, message=None):
  if (message == None):
    if (json_val == []):
      return jsonify({"msg": "Not Found"}), 404
    return jsonify(json_val), status
  else:
    return jsonify({"msg": message}), status

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5501, debug=True)