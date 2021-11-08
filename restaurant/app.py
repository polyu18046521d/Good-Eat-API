from logging import debug
from typing import Tuple
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
def insert_new_menu(store_id):
    status_query = query_store(store_id)
    if status_query == None:
        return "Restaurant Not Found", 404
    store_response, status_code = access_store_service(store_id)
    if 500 <= status_code and status_code <= 599:
        return store_response, status_code
    if status_code == 404:
        return "Restaurant Not Found", 404
    menu_response, status_code = access_menu_service(store_id)
    if status_code == 404:
        return "Restaurant Not Found", 404
    if 500 <= status_code and status_code <= 599:
        return store_response, status_code

    status = dict(status_query)
    store_info = store_response.json()[0]
    menu_info = menu_response.json()[0]
    res = store_info | status | menu_info
    return res, 200


@custom_circuitbreaker
def access_store_service(store_id):
    return requests.get(f"http://store-load-balancer:5210/{store_id}")


@custom_circuitbreaker
def access_menu_service(store_id):
    return requests.get(f"http://menu-load-balancer:5310/{store_id}")


@app.route("/<store_id>/status", methods=["POST"])
@response_helper
def update_store_status(store_id):
    status_query = query_store(store_id)
    if status_query == None:
        return "Restaurant Not Found", 404
    collection = db.access_status()
    val = dict(request.get_json())["status"]
    collection.update_one({"store_id": store_id}, {"$set": {"status": val}})
    return "", 204


@app.route("/<store_id>/menu", methods=["POST"])
@response_helper
def update_store_menu(store_id):
    status_query = query_store(store_id)
    if status_query == None:
        return "Restaurant Not Found", 404
    data = dict(request.get_json())
    producer.publish(
        json.dumps(
            {"event-type": "menu-updated", "data": {"store_id": store_id, "menu": data}}
        )
    )
    return "", 204


def query_store(store_id):
    return db.access_status().find_one({"store_id": store_id}, {"_id": 0})


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5101, debug=True)
