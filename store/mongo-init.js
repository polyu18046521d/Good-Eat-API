db.auth('comp3122', '12345');
db = db.getSiblingDB('GoodEat');

db.createCollection('stores');

for (let i = 1; i <= 100; i++) {
  const storeId = ("" + i).padStart(5, "0");

  const possibleStatus = ["OFFLINE", "ONLINE"]
  const offlineReason = ["OUT_OF_MENU_HOURS", "INVISIBLE", "PAUSED_BY_RESTAURANT"]
  const val = {
    "status": possibleStatus[i % 2],
  }
  res_status = (i % 2 == 0)
    ? { ...val, offlineReason: offlineReason[i % 3] }
    : { ...val }

  db.stores.insertOne({
    "name": "store-" + storeId,
    "store_id": storeId,
    "status": "active",
    "restaurant_status": res_status,
    "holiday_hours": [
      {
        "2020-10-10": {
          "open_time_periods": [
            {
              "start_time": "00:00",
              "end_time": "23:59"
            }
          ]
        }
      }
    ]
  });
}