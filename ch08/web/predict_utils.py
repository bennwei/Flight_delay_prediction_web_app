import sys, os, re
import pymongo
import datetime, iso8601

def process_search(results):
  """Process elasticsearch hits and return flights records"""
  records = []
  total = 0
  if results['hits'] and results['hits']['hits']:
    total = results['hits']['total']
    hits = results['hits']['hits']
    for hit in hits:
      record = hit['_source']
      records.append(record)
  return records, total

def get_navigation_offsets(offset1, offset2, increment):
  """Calculate offsets for fetching lists of flights from MongoDB"""
  offsets = {}
  offsets['Next'] = {'top_offset': offset2 + increment, 'bottom_offset':
  offset1 + increment}
  offsets['Previous'] = {'top_offset': max(offset2 - increment, 0),
 'bottom_offset': max(offset1 - increment, 0)} # Don't go < 0
  return offsets

def strip_place(url):
  """Strip the existing start and end parameters from the query string"""
  try:
    p = re.match('(.+)\?start=.+&end=.+', url).group(1)
  except AttributeError as e:
    return url
  return p

def get_flight_distance(client, origin, dest):
  """Get the distance between a pair of airport codes"""
  query = {
    "Origin": origin,
    "Dest": dest,
  }
  record = client.agile_data_science.origin_dest_distances.find_one(query)
  return record["Distance"]

def get_regression_date_args(iso_date):
  """Given an ISO Date, return the day of year, day of month, day of week as the API expects them."""
  dt = iso8601.parse_date(iso_date)
  day_of_year = dt.timetuple().tm_yday
  day_of_month = dt.day
  day_of_week = dt.weekday()
  return {
    "DayOfYear": day_of_year,
    "DayOfMonth": day_of_month,
    "DayOfWeek": day_of_week,
  }

def get_current_timestamp():
  iso_now = datetime.datetime.now().isoformat()
  return iso_now
