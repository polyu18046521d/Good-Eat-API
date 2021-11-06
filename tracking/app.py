from flask import Flask, jsonify, request
from functools import wraps
from datetime import datetime
import requests
import json

from circuitbreaker import custom_circuitbreaker
import producer
import db

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


def response_helper(func):
    @wraps(func)
    def helper(*args, **kwargs):
        val, status = func(*args, **kwargs)
        if isinstance(val, str):
            return jsonify({"msg": val}), status
        else:
            if val == []:
                return jsonify({"msg": "Not Found"}), 404
            return jsonify(val), status

    return helper


@app.route("/<order_id>", methods=["GET"])
@response_helper
@custom_circuitbreaker
def order_query(order_id):
    order_response = requests.get(f"http://order-api:5006/{order_id}", timeout=0.001)
    if order_response.status_code == 404:
        return "Not Found", 404
    order = order_response.json()[0]
    status = db.access_tracking().find_one({"order_id": order_id}, {"_id": 0})
    res = order | status
    return res, 200


@app.route("/", methods=["POST"])
@response_helper
def add_order():
    data = dict(request.get_json())
    data["timestamp"] = datetime.ctime(datetime.now())
    order_id = str(hash(json.dumps(data)))

    data["order_id"] = order_id
    producer.publish(json.dumps({"event-type": "order-updated", "data": data}))
    db.access_tracking().insert_one({"order_id": order_id, "status": "PENDING"})
    return {"order_id": order_id}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5401)
