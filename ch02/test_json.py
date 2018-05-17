#!/usr/bin/env python
#
# How to read and write JSON and JSON Lines files using Python
#
import sys, os, re
import json
import codecs

ary_of_objects = [
  {'name': 'Russell Jurney', 'title': 'CEO'},
  {'name': 'Muhammad Imran', 'title': 'VP of Marketing'},
  {'name': 'Fe Mata', 'title': 'Chief Marketing Officer'},
]

path = r"data\example_name_titles_daily.json\2016-12-01\test.jsonl"

#
# Write our objects to jsonl
#
f = codecs.open(path, 'w', 'utf-8')
for row_object in ary_of_objects:
  # ensure_ascii=False is essential or errors/corruption will occur
  json_record = json.dumps(row_object, ensure_ascii=False)
  f.write(json_record + "\n")
f.close()

print("Wrote JSON Lines file /tmp/test.jsonl")

#
# Read this jsonl file back into objects
#
ary_of_objects = []
f = codecs.open(path, "r", "utf-8")
for line in f:
  record = json.loads(line.rstrip("\n|\r"))
  ary_of_objects.append(record)
print(ary_of_objects)
print("Read JSON Lines file /tmp/test.jsonl")

#
# Utility functions to read and write json and jsonl files
#
def write_json_file(obj, path):
  '''Dump an object and write it out as json to a file.'''
  f = codecs.open(path, 'w', 'utf-8')
  f.write(json.dumps(obj, ensure_ascii=False))
  f.close()

def write_json_lines_file(ary_of_objects, path):
  '''Dump a list of objects out as a json lines file.'''
  f = codecs.open(path, 'w', 'utf-8')
  for row_object in ary_of_objects:
    json_record = json.dumps(row_object, ensure_ascii=False)
    f.write(json_record + "\n")
  f.close()

def read_json_file(path):
  '''Turn a normal json file (no CRs per record) into an object.'''
  text = codecs.open(path, 'r', 'utf-8').read()
  return json.loads(text)

def read_json_lines_file(path):
  '''Turn a json cr file (CRs per record) into an array of objects'''
  ary = []
  f = codecs.open(path, "r", "utf-8")
  for line in f:
    record = json.loads(line.rstrip("\n|\r"))
  return ary
