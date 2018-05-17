from pymongo import MongoClient

client = MongoClient()

record = {"foo": "bar"}

client.agile_data_science.collection_two.insert_one(record)

record2 = client.agile_data_science.collection_one.find_one(
  {
    "foo": "bar"
  }
)
