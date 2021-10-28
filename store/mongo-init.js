db.auth('comp3122', '12345');
db = db.getSiblingDB('GoodEat');

db.createCollection('stores');

for (let i = 1; i <= 100; i++) {
  const storeId = ("" + i).padStart(5, "0");

  db.stores.insertOne({
    "name": "store-" + storeId,
    "store_id": storeId,
  });
}