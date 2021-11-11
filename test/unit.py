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
        #tbc
        return token
    
    def test_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res.json()
        assert res.status_code == 200
    #Restaurant service    
    def test_eats_storeid(self):
        res0 = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res0.json()
        #token = json.dumps(json_data)
       # token_helper = json_data["access_token"]
        #username = request.json.get("username", None)
        #token = res0.json.post("access_token",None)
        
        data = json.dumps(json_data)
        count0 =0
        while data[count0]!=':':
	        count0=count0+1

        count1 = 0
        while data[count1]!='}':
	        count1=count1+1

        token=data[count0+3:count1-1]
        whole_token="Bearer " + token
        
        
        #token_helper = json.loads(json_data)
        #token = token_helper["access_token"]
        headers = {'Authorization': whole_token}
        #headers = {'Authorization':"Bearer" + token_helper}
        res = requests.get(self.url_helper("/eats/00001"),headers=headers)
        #json_data = res.json()
        assert res.status_code == 200
		   
    def test_eats_storeid_menu(self):
        res0 = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res0.json()
                
        data = json.dumps(json_data)
        count0 =0
        while data[count0]!=':':
	        count0=count0+1

        count1 = 0
        while data[count1]!='}':
	        count1=count1+1

        token=data[count0+3:count1-1]
        
        headers = {'Authorization':"Bearer " + token,'Content-Type': 'application/json'}
        res = requests.post(
		self.url_helper("/eats/00001/menu"), json={"menu_id": "D","name": "Set Lunch D","price": "150"}
	    )   
        assert res.status_code == 200
	# Order service	   
    def test_eats_order_orderid(self):
        res0 = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res0.json()
                
        data = json.dumps(json_data)
        count0 =0
        while data[count0]!=':':
	        count0=count0+1

        count1 = 0
        while data[count1]!='}':
	        count1=count1+1

        token=data[count0+3:count1-1]
        
        headers = {'Authorization':"Bearer " + token}
        res = requests.get(
		    self.url_helper("/eats/order/000011")
	    )   
        assert res.status_code == 200

    def test_eats_order(self):
        res0 = requests.post(
            self.url_helper("/login"), json={"username":"test","password":"test"}
        )
        json_data = res0.json()
                
        data = json.dumps(json_data)
        count0 =0
        while data[count0]!=':':
	        count0=count0+1

        count1 = 0
        while data[count1]!='}':
	        count1=count1+1

        token=data[count0+3:count1-1]
        
        headers = {'Authorization':"Bearer " + token,'Content-Type': 'application/json'}
        res = requests.post(
		self.url_helper("/eats/order"), json={
                                                "store_id": "00001",
                                                "details": [
                                                    {
                                                        "menu_id": "A",
                                                        "count": 1
                                                    }
                                                ]             
                                             }
	    )   
        assert res.status_code == 200        

    def test_eats_order_orderid_status(self):
              
        headers = {'Content-Type': 'application/json'}
        res = requests.post(
		self.url_helper("/eats/order/000011/status"), json={"status": "ACCEPTED"}
	    )   
        assert res.status_code == 200
