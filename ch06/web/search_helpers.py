import sys, os, re

# Process elasticsearch hits and return flights records
def process_search(results):
  records = []
  total = 0
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
    p = re.match('(.+)\?start=.+&end=.+', url).group(1)
  except AttributeError as e:
    return url
  return p
