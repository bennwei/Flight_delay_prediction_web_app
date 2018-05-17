from flask import Flask
from pymongo import MongoClient
import bson.json_util

# Set up Flask
app = Flask(__name__)

# Set up Mongo
client = MongoClient() # defaults to localhost
db = client.agile_data_science

# Fetch from/to totals, given a pair of email addresses
@app.route("/executive/<name>")
def executive(name):
  executive = db.executives.find({"name": name})
  return bson.json_util.dumps(list(executive))

if __name__ == "__main__": app.run(debug=True)