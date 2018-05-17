from flask import Flask, render_template, request
from pymongo import MongoClient
from bson import json_util

# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient()


# Controller: Fetch all flights between cities on a given day and display them
@app.route("/flights/<origin>/<dest>/<flight_date>")
def list_flights(origin, dest, flight_date):
    flights = client.agile_data_science.on_time_performance.find(
        {
            'Origin': origin,
            'Dest': dest,
            'FlightDate': flight_date
        },
        sort=[
            ('DepTime', 1),
            ('ArrTime', 1),
        ]
    )
    flight_count = flights.count()

    return render_template('flights.html', flights=flights, flight_date=flight_date, flight_count=flight_count)

if __name__ == "__main__":
  app.run(debug=True)