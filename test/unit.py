#from flask import Flask
import json
#from flask_pytest_example.handlers.routes import configure_routes
import requests

class TestClass:
    def url_helper(self, path):
        return "http://localhost" + path
    
    def parse(self, obj):
        if isinstance(obj, dict):
            return sorted((k, self.parse(v)) for k, v in obj.items())
        if isinstance(obj, list):
            return sorted(self.parse(x) for x in obj)
        else:
            return obj
    
    def token_helper(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        token = json.dumps(json_data)
        return token["access_token"]
    
    def test_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        assert res.status_code == 200
        
    def test_eats_storeid(self):
        res0 = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        #json_data = res0.json()
        #token = json.dumps(json_data)
        #token_helper = json_data("access_token")
        #username = request.json.get("username", None)
        token = res0.json.post("access_token",None)
        headers = {'Authorization':"Bearer" + token}
        res = requests.get(self.url_helper("/eats/00001"),headers=headers)
        json_data = res.json()
        assert res.status_code == 200
        

