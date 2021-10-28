db.auth('comp3122', '12345');
db = db.getSiblingDB('GoodEat');

db.createCollection('menu');

for (let i = 1; i <= 100; i++) {
  const storeId = ("" + i).padStart(5, "0");

  db.menu.insertOne({
    "store_id": storeId,
    "menus": [
      {
        "menu_id": "A",
        "name": "Drink A",
        "price": "30"
      },
      {
        "menu_id": "B",
        "name": "Drink B",
        "price": "36"
      }
    ]
  });
}