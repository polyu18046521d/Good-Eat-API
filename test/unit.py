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

    def get_jwt_token(self):
        res = requests.post(
            self.url_helper("/login"), json={"username": "test", "password": "test"}
        )
        return res.json().get("access_token")

    def auth_header(self):
        token = self.get_jwt_token()
        return {"Authorization": f"Bearer {token}"}

    def test_valid_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username": "test", "password": "test"}
        )
        json_data = res.json()
        assert res.status_code == 200
        assert res.headers["content-type"] == "application/json"
        assert "access_token" in json_data

    def test_invalid_login(self):
        res = requests.post(
            self.url_helper("/login"), json={"username": "test", "password": "123"}
        )
        json_data = res.json()
        assert res.status_code == 401
        assert res.headers["content-type"] == "application/json"
        assert self.parse(json_data) == self.parse({"msg": "Bad username or password"})

    # Restaurant service
    # def test_eats_storeId(self):
    #     res = requests.get(
    #         self.url_helper("/eats/00001"),
    #         headers=self.auth_header(),
    #     )
    #     json_data = res.json()
    #     assert res.status_code == 200
    #     assert res.headers["content-type"] == "application/json"
    #     assert self.parse(json_data) == self.parse(
    #         {
    #             "menus": [
    #                 {"menu_id": "A", "name": "Drink A", "price": 30.0},
    #                 {"menu_id": "B", "name": "Drink B", "price": 36.0},
    #             ],
    #             "name": "store-00001",
    #             "status": "ONLINE",
    #             "store_id": "00001",
    #         }
    #     )

    def test_eats_storeId_menu(self):
        res = requests.post(
            self.url_helper("/eats/00001/menu"),
            json={"menu_id": "D", "name": "Set Lunch D", "price": "150"},
            headers=self.auth_header(),
        )
        assert res.status_code == 204
        assert res.headers["content-type"] == "application/json"
        assert res.content == b""

    # Order service
    # def test_eats_order_orderId(self):
    #     res = requests.get(
    #         self.url_helper("/eats/order/000011"),
    #         headers=self.auth_header(),
    #     )
    #     json_data = res.json()
    #     assert res.status_code == 200
    #     assert res.headers["content-type"] == "application/json"
    #     assert self.parse(json_data) == self.parse(
    #         {
    #             "details": [{"count": 1.0, "menu_id": "A"}],
    #             "order_id": "000011",
    #             "status": "PENDING",
    #             "store_id": "00001",
    #         }
    #     )

    def test_eats_order(self):
        res = requests.post(
            self.url_helper("/eats/order"),
            json={"store_id": "00001", "details": [{"menu_id": "A", "count": 1}]},
            headers=self.auth_header(),
        )
        json_data = res.json()
        assert res.status_code == 201
        assert res.headers["content-type"] == "application/json"
        assert "order_id" in json_data

    def test_eats_order_orderId_status(self):
        res = requests.post(
            self.url_helper("/eats/order/000011/status"),
            json={"status": "ACCEPTED"},
            headers=self.auth_header(),
        )
        assert res.status_code == 204
        assert res.headers["content-type"] == "application/json"
        assert res.content == b""
