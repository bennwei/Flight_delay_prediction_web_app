from flask import Flask, render_template, request
from pymongo import MongoClient
from bson import json_util

# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient()

# Chapter 5 controller: Fetch a flight and display it
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
  
  return render_template('flight.html', flight=flight)

# Chapter 5 controller: Fetch all flights between cities on a given day and display them
@app.route("/flights/<origin>/<dest>/<flight_date>")
def list_flights(origin, dest, flight_date):
  
  flights = client.agile_data_science.on_time_performance.find(
    {
      'Origin': origin,
      'Dest': dest,
      'FlightDate': flight_date
    },
    sort = [
      ('DepTime', 1),
      ('ArrTime', 1),
    ]
  )
  flight_count = flights.count()
  
  return render_template('flights.html', flights=flights, flight_date=flight_date, flight_count=flight_count)

# Controller: Fetch a flight table
@app.route("/total_flights")
def total_flights():
  total_flights = client.agile_data_science.flights_by_month.find({},
    sort = [
      ('Year', 1),
      ('Month', 1)
    ])

  # total_flights = client.agile_data_science.flights_by_month.find().sort({'Year': pymongo.ASCENDING, 'Month': pymongo.ASCENDING})
  return render_template('total_flights.html', total_flights=total_flights)

# Serve the chart's data via an asynchronous request (formerly known as 'AJAX')
@app.route("/total_flights.json")
def total_flights_json():
  total_flights = client.agile_data_science.flights_by_month.find({}, 
    sort = [
      ('Year', 1),
      ('Month', 1)
      # ('Year', client.ASCENDING),
      # ('Month', client.ASCENDING)
    ])
  return json_util.dumps(total_flights, ensure_ascii=False)

# Controller: Fetch a flight chart
@app.route("/total_flights_chart")
def total_flights_chart():
  total_flights = client.agile_data_science.flights_by_month.find({}, 
    sort = [
      ('Year', 1),
      ('Month', 1)

    ])
  return render_template('total_flights_chart.html', total_flights=total_flights)

# Controller: Fetch a flight and display it
@app.route("/airplane/flights/<tail_number>")
def flights_per_airplane(tail_number):
  flights = client.agile_data_science.flights_per_airplane.find_one({'TailNum': tail_number})
  return render_template('flights_per_airplane.html', flights=flights, tail_number=tail_number)

if __name__ == "__main__":
  app.run(debug=True)
