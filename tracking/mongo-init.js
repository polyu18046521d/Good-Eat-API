db.auth('comp3122', '12345');
db = db.getSiblingDB('GoodEat');

db.createCollection('tracking');

for (let i = 1; i <= 5; i++) {
  const storeId = ("" + i).padStart(5, "0");

  for (let j = 0; j < 2; j++) {
    db.tracking.insertOne({
      "order_id": storeId + (j+1),
      "status": "PENDING"
    });
  }
}