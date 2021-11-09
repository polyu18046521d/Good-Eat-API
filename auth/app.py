from flask import Flask, request, jsonify, Response
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
import json
import redis

app = Flask(__name__)

jwt = JWTManager()

app.config["JWT_SECRET_KEY"] = "comp3122-group-3"
jwt.init_app(app)


@app.route("/")
def sample():
    return "Auth service"


@app.route("/login", methods=["POST"])
def login():
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request login",
        )
    )

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if username != "test" or password != "test":
        app.logger.warn(
            log_helper(
                trace_id,
                get_span_id(),
                status_code=401,
                url=request.url,
                details="login failed",
            )
        )
        return jsonify({"msg": "Bad username or password"}), 401

    app.logger.info(
        log_helper(
            trace_id,
            get_span_id(),
            status_code=200,
            url=request.url,
            details="login success",
        )
    )
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)


@app.route("/verify", methods=["GET"])
@jwt_required()
def verify():
    trace_id, span_id = get_trace_id(), get_span_id()
    app.logger.info(
        log_helper(
            trace_id,
            span_id,
            method=request.method,
            url=request.url,
            details="request verify",
        )
    )
    # current_user = get_jwt_identity()
    res = Response("valid token", 200)
    res.headers['Trace-Id'] = trace_id
    return res


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
    span_id = f"AUTH-{r.incr('auth_span', 1)}"
    return span_id


if __name__ == "__main__":
    import logging, logging.config, yaml

    logging.config.dictConfig(yaml.safe_load(open("logging.conf")))
    log = logging.getLogger("werkzeug")
    log.disabled = True
    app.run(host="0.0.0.0", port=5001)
