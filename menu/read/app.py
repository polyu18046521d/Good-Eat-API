from logging import debug
from flask import Flask, jsonify, request
import db
import redis
import json

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/<store_id>", methods=["GET"])
def get_store_all_menu(store_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request menu",
        )
    )
    menu = db.access_menu()
    res = list(menu.find({"store_id": store_id}, {"_id": 0}))

    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=200,
            url=request.url,
            details="request menu success",
        )
    )
    return response_helper(200, res)


def response_helper(status, json_val, message=None):
    if message == None:
        return jsonify(json_val), status
    else:
        return jsonify({"msg": message}), status


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
    span_id = f"MENU-{r.incr('menu_span', 1)}"
    return span_id


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5301)
