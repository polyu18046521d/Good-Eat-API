db.auth('comp3122', '12345');
db = db.getSiblingDB('GoodEat');

db.createCollection('status');

for (let i = 1; i <= 100; i++) {
  const storeId = ("" + i).padStart(5, "0");

  db.status.insertOne({
    "store_id": storeId,
    "status": (i % 2)? "ONLINE": "CLOSED"
  });
}