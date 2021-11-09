import json
from flask import Flask, abort, jsonify, request
import db
import producer
import redis
import json

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/<store_id>", methods=["POST"])
def insert_new_menu(store_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request upload menu",
        )
    )
    data = dict(request.get_json())
    menu = db.access_menu()
    menu.update_one({"store_id": store_id}, {"$push": {"menus": data}})
    producer.publish(
        json.dumps(
            {"event-type": "menu-updated", "data": {"store_id": store_id, "menu": data}}
        )
    )
    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=204,
            url=request.url,
            details="request upload menu success",
        )
    )
    return response_helper(204, "")


def response_helper(status, json_val, message=None):
    if message == None:
        if json_val == []:
            return jsonify({"msg": "Not Found"}), 404
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
    app.run(host="0.0.0.0", port=5300)
