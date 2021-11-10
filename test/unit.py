from flask import Flask
import json
from flask_pytest_example.handlers.routes import configure_routes

def test_login():
    #coonnect to flask
    app = Flask(__name__)
    configure_routes(app)
    client = app.test_client()
    #test with the following url
    url = '/login'
    #test data
    mock_request_data = {"username":"test","password":"test"}
    #send request and obtain response
    response = client.post(url, data=json.dumps(mock_request_data))
    #determine the status code of the response is correct
    assert response.status_code == 200
