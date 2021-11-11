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
       		res0 = requests.post(self.url_helper("/login"), json={"username":"test","password":"test"})
        	json_data = res.json()
        	data = json.dumps(json_data)
	
        	count0 =0
        	while data[count0]!=':':
			count0=count0+1

		count1 = 0
		while data[count1]!='}':
			count1=count1+1
		
		token=data[count0+3:count1-1]
	return token
    
    def test_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        assert res.status_code == 200
        
    def test_eats_storeid(self):
       
        headers = {'Authorization':"Bearer " + self.token_helper()}
        #headers = {'Authorization':"Bearer" + token_helper}
        res = requests.get(self.url_helper("/eats/00001"),headers=headers)
        #json_data = res.json()
        assert res.status_code == 200
        

