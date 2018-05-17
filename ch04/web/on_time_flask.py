from flask import Flask, render_template, request
from pymongo import MongoClient
from bson import json_util

# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient()

# Controller: Fetch an email and display it
@app.route("/on_time_performance")
def on_time_performance():
  
  carrier = request.args.get('Carrier')
  flight_date = request.args.get('FlightDate')
  flight_num = request.args.get('FlightNum')
  
  flight = client.agile_data_science.on_time_performance.find_one({
    'Carrier': carrier,
    'FlightDate': flight_date,
    'FlightNum': flight_num
  })
  
  return json_util.dumps(flight)

if __name__ == "__main__":
  app.run(debug=True)
  print(on_time_performance())
