from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)

jwt = JWTManager()

app.config['JWT_SECRET_KEY'] = 'comp3122-group-3'
jwt.init_app(app)

@app.route("/")
def sample():
  return "Auth service"

@app.route("/login", methods=["POST"])
def login():
  username = request.json.get('username', None) 
  password = request.json.get('password', None) 

  if username != 'test' or password != 'test': 
      return jsonify({"msg": "Bad username or password"}), 401

  access_token = create_access_token(identity=username)
  return jsonify(access_token=access_token)

@app.route("/verify", methods=["GET"])
@jwt_required()
def verify():
  current_user = get_jwt_identity()
  return jsonify(logged_in_as=current_user), 200


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)