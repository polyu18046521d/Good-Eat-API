from flask import Flask, abort, jsonify, request
import db

from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)


@app.route("/<store_id>", methods=["GET"])
def get_store_all_menu(store_id):
    menu = db.access_menu()
    res = list(menu.find({"store_id": store_id}, {"_id": 0}))
    return response_helper(200, res)


def response_helper(status, json_val, message=None):
    if message == None:
        if json_val == []:
            return jsonify({"msg": "Not Found"}), 404
        return jsonify(json_val), status
    else:
        return jsonify({"msg": message}), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5301)
