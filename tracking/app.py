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


@app.after_request
def log_after_request(res):
    if 500 <= res.status_code and res.status_code <= 599:
        app.logger.error(
            log_helper(status_code=res.status_code, details="server error")
        )
    else:
        app.logger.info(log_helper(status_code=res.status_code, details="successful"))
    return res


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
    app.logger.info(
        log_helper(method="GET", url=f"http://order-load-balancer:5510/{order_id}")
    )
    order_response = requests.get(f"http://order-load-balancer:5510/{order_id}")
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


def log_helper(status_code="", method="", url="", details=""):
    return json.dumps(
        {"status_code": status_code, "method": method, "url": url, "details": details}
    )


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5401)
