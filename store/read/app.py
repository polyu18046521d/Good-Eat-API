from flask import Flask, jsonify
import db
import json

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/", methods=["GET"])
def get_all_stores():
    stores = db.access_stores()
    res = list(stores.find({}, {"_id": 0}))
    return response_helper(200, res)


@app.route("/<store_id>", methods=["GET"])
def get_one_store(store_id):
    stores = db.access_stores()
    res = list(stores.find({"store_id": store_id}, {"_id": 0}))
    return response_helper(200, res)


def response_helper(status, json_val, message=None):
    if message == None:
        if json_val == []:
            return jsonify({"msg": "Not Found"}), 404
        return jsonify(json_val), status
    else:
        return jsonify({"msg": message}), status

def log_helper(status_code="", method="", url="", details=""):
    return json.dumps(
        {"status_code": status_code, "method": method, "url": url, "details": details}
    )


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5201)
