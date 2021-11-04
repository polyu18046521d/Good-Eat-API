db.auth('comp3122', '12345');
db = db.getSiblingDB('GoodEat');

db.createCollection('order');

for (let i = 1; i <= 5; i++) {
  const storeId = ("" + i).padStart(5, "0");

  for (let j = 0; j < 2; j++) {
    db.order.insertOne({
      "order_id": storeId + (j + 1),
      "store_id": storeId,
      "details": [
        {
          "menu_id": "A",
          "count": 1
        }
      ]
    });
  }
}