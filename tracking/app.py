from flask import Flask, jsonify, request, Response
from functools import wraps
from datetime import datetime
import requests
import json
import redis

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


@app.route("/<order_id>", methods=["GET"])
@response_helper
def order_query(order_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request a order",
        )
    )
    status = db.access_tracking().find_one({"order_id": order_id}, {"_id": 0})
    if status == None:
        app.logger.info(
            log_helper(
                trace_id,
                get_span_id(),
                status_code=404,
                url=request.url,
                details="request order not found in tracking db",
            )
        )
        return "Order Not Found", 404

    order_response, status_code = access_order_service(order_id, trace_id)
    if 500 <= status_code and status_code <= 599:
        app.logger.info(
            log_helper(
                trace_id,
                get_span_id(),
                status_code=status_code,
                url=request.url,
                details="order service connection failed",
            )
        )
        return order_response, status_code
    if status_code == 404:
        app.logger.info(
            log_helper(
                trace_id,
                get_span_id(),
                status_code=404,
                url=request.url,
                details="request order not found in order db",
            )
        )
        return "Order Not Found", 404

    order = order_response.json()[0]
    res = order | status
    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=200,
            url=request.url,
            details="request order success",
        )
    )
    return res, 200


@app.route("/", methods=["POST"])
@response_helper
def add_order():
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request create a new order",
        )
    )

    data = dict(request.get_json())
    data["timestamp"] = datetime.ctime(datetime.now())
    order_id = str(abs(hash(json.dumps(data))))

    data["order_id"] = order_id
    producer.publish(json.dumps({"event-type": "order-updated", "data": data}))
    db.access_tracking().insert_one({"order_id": order_id, "status": "PENDING"})

    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=201,
            url=request.url,
            details="request order-updated Event Created",
        )
    )
    return {"order_id": order_id}, 201


@app.route("/<order_id>/status", methods=["POST"])
@response_helper
def update_order_status(order_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request update order status",
        )
    )

    req_json = dict(request.get_json())
    new_status = req_json.get("status")
    if new_status == None:
        return "Invalid request body", 404
    order_status = db.access_tracking().find_one({"order_id": order_id}, {"_id": 0})
    if order_status == None:
        return "Order Id Not Found", 404
    db.access_tracking().update_one(
        {"order_id": order_id}, {"$set": {"status": new_status}}
    )
    return "", 204


@custom_circuitbreaker
def access_order_service(order_id, trace_id):
    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            method="GET",
            url=f"http://order-load-balancer:5510/{order_id}",
            details="request order service",
        )
    )
    return requests.get(
        f"http://order-load-balancer:5510/{order_id}",
        headers={"trace-id": str(trace_id)},
    )


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
    span_id = f"TRACKING-{r.incr('tracking_span', 1)}"
    return span_id


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5401)
