from flask import Flask, jsonify, request
from functools import wraps
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


@app.route("/<store_id>", methods=["GET"])
@response_helper
@custom_circuitbreaker
def insert_new_menu(store_id):
    status = dict(db.access_status().find_one({"store_id": store_id}, {"_id": 0}))
    store_info = requests.get(f"http://store-read-api:5001/{store_id}").json()[0]
    menu_info = requests.get(f"http://menu-read-api:5002/{store_id}").json()[0]
    res = store_info | status | menu_info
    return res, 200


@app.route("/<store_id>/status", methods=["POST"])
@response_helper
def update_store_status(store_id):
    collection = db.access_status()
    val = dict(request.get_json())["status"]
    collection.update_one({"store_id": store_id}, {"$set": {"status": val}})
    return "", 204


@app.route("/<store_id>/menu", methods=["POST"])
@response_helper
def update_store_menu(store_id):
    data = dict(request.get_json())
    producer.publish(
        json.dumps(
            {"event-type": "menu-updated", "data": {"store_id": store_id, "menu": data}}
        )
    )
    return "", 204


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5101)
