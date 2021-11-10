#from flask import Flask
#import json
#from flask_pytest_example.handlers.routes import configure_routes
import requests

class TestClass:
    def url_helper(self, path):
        return "http://localhost" + path
    
    def test_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        assert res.status_code == 200
        #assert res.headers["content-type"] == "application/json"
        #assert self.parse(json_data) == self.parse({"message": "Student Created"})
        
        

