from functools import wraps
from flask import Flask, abort, jsonify, request
import db
import redis
import json

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
def get_order(order_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request order",
        )
    )
    res = list(db.access_order().find({"order_id": order_id}, {"_id": 0}))
    if res == []:
        app.logger.info(
            log_helper(
                trace_id,
                get_span_id(),
                status_code=404,
                url=request.url,
                details="request order not found",
            )
        )
        return "Order Not Found", 404
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
    span_id = f"ORDER-{r.incr('order_span', 1)}"
    return span_id


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5501)
