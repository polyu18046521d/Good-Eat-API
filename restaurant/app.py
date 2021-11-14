from flask import Flask, jsonify, request, Response
from functools import wraps
import requests
import redis
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
        if isinstance(val, Response):
            return val
        elif isinstance(val, str):
            return jsonify({"msg": val}), status
        else:
            if val == []:
                return jsonify({"msg": "Not Found"}), 404
            return jsonify(val), status

    return helper


@app.route("/<store_id>", methods=["GET"])
@response_helper
def insert_new_menu(store_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request restaurant store menu",
        )
    )
    status_query = query_store(store_id)
    if status_query == None:
        return "Restaurant Not Found", 404
    store_response, status_code = access_store_service(store_id, trace_id)
    if 500 <= status_code and status_code <= 599:
        return store_response, status_code
    if status_code == 404:
        return "Restaurant Not Found", 404
    menu_response, status_code = access_menu_service(store_id, trace_id)
    if status_code == 404:
        return "Restaurant Not Found", 404
    if 500 <= status_code and status_code <= 599:
        return menu_response, status_code

    status = dict(status_query)
    store_info = store_response.json()[0]
    menu_info = menu_response.json()[0]
    res = store_info | status | menu_info
    return res, 200


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

@custom_circuitbreaker
def access_store_service(store_id, trace_id):
    return requests.get(
        f"http://store-load-balancer:5210/{store_id}", headers={"trace-id": str(trace_id)}
    )


@custom_circuitbreaker
def access_menu_service(store_id, trace_id):
    return requests.get(
        f"http://menu-load-balancer:5310/{store_id}", headers={"trace-id": str(trace_id)}
    )




def query_store(store_id):
    return db.access_status().find_one({"store_id": store_id}, {"_id": 0})


def log_helper(trace_id, span_id, status_code="", method="", url="", details=""):
    return json.dumps(
        {
            "trace_id": trace_id,
            "span_id": span_id,
            "status_code": status_code,
            "method": method,
            "url": url,
            "details": details,
        }
    )


def get_trace_id():
    r = redis.Redis(host="redis-db", decode_responses=True)
    trace_id = request.headers.get("trace-id")
    if trace_id == None:
        trace_id = r.incr("trace_id", 1)
    else:
        trace_id = int(trace_id)
    return trace_id


def get_span_id():
    r = redis.Redis(host="redis-db", decode_responses=True)
    span_id = f"RESTAURANT-{r.incr('restaurant_span', 1)}"
    return span_id


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5101)
