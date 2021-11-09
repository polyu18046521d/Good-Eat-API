from flask import Flask, jsonify, request
import db
import json
import redis

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/", methods=["GET"])
def get_all_stores():
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request all stores infomation",
        )
    )

    stores = db.access_stores()
    res = list(stores.find({}, {"_id": 0}))
    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=200,
            url=request.url,
            details="request stores success",
        )
    )

    return response_helper(200, res)


@app.route("/<store_id>", methods=["GET"])
def get_one_store(store_id):
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request a specific store infomation",
        )
    )

    stores = db.access_stores()
    res = list(stores.find({"store_id": store_id}, {"_id": 0}))
    if res == []:
        app.logger.info(
            log_helper(
                trace_id,
                get_span_id(),
                status_code=404,
                url=request.url,
                details="request Store Not Found",
            )
        )
        return response_helper(404, "Store Not Found")
    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=200,
            url=request.url,
            details="request Store success",
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
    span_id = f"STORE-{r.incr('store_span', 1)}"
    return span_id


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5201)
