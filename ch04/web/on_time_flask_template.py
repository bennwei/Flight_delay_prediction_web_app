import sys, os, re
from flask import Flask, render_template, request
from pymongo import MongoClient
from bson import json_util
import config
import json

from pyelasticsearch import ElasticSearch
elastic = ElasticSearch(config.ELASTIC_URL)

# Process elasticsearch hits and return flights records
def process_search(results):
  records = []
  if results['hits'] and results['hits']['hits']:
    total = results['hits']['total']
    hits = results['hits']['hits']
    for hit in hits:
      record = hit['_source']
      records.append(record)
  return records, total

# Calculate offsets for fetching lists of flights from MongoDB
def get_navigation_offsets(offset1, offset2, increment):
  offsets = {}
  offsets['Next'] = {'top_offset': offset2 + increment, 'bottom_offset': 
  offset1 + increment}
  offsets['Previous'] = {'top_offset': max(offset2 - increment, 0), 
 'bottom_offset': max(offset1 - increment, 0)} # Don't go < 0
  return offsets

# Strip the existing start and end parameters from the query string
def strip_place(url):
  try:
    p = re.match('(.+)&start=.+&end=.+', url).group(1)
  except AttributeError as e:
    return url
  return p

# Set up Flask and Mongo
app = Flask(__name__)
client = MongoClient()

# Controller: Fetch a flight and display it
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

# Controller: Fetch all flights between cities on a given day and display them
@app.route("/flights/<origin>/<dest>/<flight_date>")
def list_flights(origin, dest, flight_date):
  
  start = request.args.get('start') or 0
  start = int(start)
  end = request.args.get('end') or config.RECORDS_PER_PAGE
  end = int(end)
  width = end - start
  
  nav_offsets = get_navigation_offsets(start, end, config.RECORDS_PER_PAGE)
  
  flights = client.agile_data_science.on_time_performance.find(
    {
      'Origin': origin,
      'Dest': dest,
      'FlightDate': flight_date
    },
    sort = [
      ('DepTime', 1),
      ('ArrTime', 1)
    ]
  )
  flight_count = flights.count()
  flights = flights.skip(start).limit(width)
    
  return render_template(
    'flights.html', 
    flights=flights, 
    flight_date=flight_date, 
    flight_count=flight_count,
    nav_path=request.path,
    nav_offsets=nav_offsets
    )

@app.route("/flights/search")
@app.route("/flights/search/")
def search_flights():
  
  # Search parameters
  carrier = request.args.get('Carrier')
  flight_date = request.args.get('FlightDate')
  origin = request.args.get('Origin')
  dest = request.args.get('Dest')
  tail_number = request.args.get('TailNum')
  flight_number = request.args.get('FlightNum')
  
  # Pagination parameters
  start = request.args.get('start') or 0
  start = int(start)
  end = request.args.get('end') or config.RECORDS_PER_PAGE
  end = int(end)
  
  print(request.args)
  # Navigation path and offset setup
  nav_path = strip_place(request.url)
  nav_offsets = get_navigation_offsets(start, end, config.RECORDS_PER_PAGE)
  
  # Build the base of our elasticsearch query
  query = {
    'query': {
      'bool': {
        'must': []}
    },
    # 'sort': [
    #   {'FlightDate': {'order': 'asc', 'ignore_unmapped' : True} },
    #   {'DepTime': {'order': 'asc', 'ignore_unmapped' : True} },
    #   {'Carrier': {'order': 'asc', 'ignore_unmapped' : True} },
    #   {'FlightNum': {'order': 'asc', 'ignore_unmapped' : True} },
    #   '_score'],

    # 'sort': [
    #   {'FlightDate': {'order': 'asc', 'ignore_unmapped': 'string'}},
    #   {'DepTime': {'order': 'asc', 'ignore_unmapped': 'string'}},
    #   {'Carrier': {'order': 'asc', 'ignore_unmapped': 'string'}},
    #   {'FlightNum': {'order': 'asc', 'ignore_unmapped': 'string'}},
    #   '_source'],
    # 'sort': [{'FlightDate': 'asc'}, {'DepTime': 'asc'}, {'Carrier': 'asc'}, {'FlightNum': 'asc'}, '_source'],

    'from': start,
    'size': config.RECORDS_PER_PAGE
  }
  
  # Add any search parameters present
  if carrier:
    query['query']['bool']['must'].append({'match': {'Carrier': carrier}})
  if flight_date:
    query['query']['bool']['must'].append({'match': {'FlightDate': flight_date}})
  if origin: 
    query['query']['bool']['must'].append({'match': {'Origin': origin}})
  if dest: 
    query['query']['bool']['must'].append({'match': {'Dest': dest}})
  if tail_number: 
    query['query']['bool']['must'].append({'match': {'TailNum': tail_number}})
  if flight_number: 
    query['query']['bool']['must'].append({'match': {'FlightNum': flight_number}})
  
  # Query elasticsearch, process to get records and count
  print("QUERY")
  print(carrier, flight_date, origin, dest, tail_number, flight_number)
  print(json.dumps(query))
  results = elastic.search(query)
  flights, flight_count = process_search(results)
  
  # Persist search parameters in the form template
  return render_template(
    'search.html', 
    flights=flights, 
    flight_date=flight_date, 
    flight_count=flight_count,
    nav_path=nav_path,
    nav_offsets=nav_offsets,
    carrier=carrier,
    origin=origin,
    dest=dest,
    tail_number=tail_number,
    flight_number=flight_number
    )

if __name__ == "__main__":
  app.run(debug=True)

