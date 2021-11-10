#from flask import Flask
#import json
#from flask_pytest_example.handlers.routes import configure_routes
import requests

class TestClass:
    def url_helper(self, path):
        return "http://localhost" + path
    
    def token_helper(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        return json_data("access_token")
    
    def test_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        assert res.status_code == 200
        
    def test_eats_storeid(self):
        headers = {'Authorization':"Bearer" + token_helper()}
        res = requests.get(self.url_helper("/eats/00001"),headers=headers)
        json_data = res.json()
        assert res.status_code == 200
        

