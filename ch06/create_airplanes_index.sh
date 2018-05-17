#!/bin/bash

# Create the entire agile_data_science index
curl -XPUT 'http://localhost:9200/agile_data_science/'

# Create the mapping to make search results sort right
curl -XPUT 'http://localhost:9200/agile_data_science/_mapping/airplane' --data @airplanes_mapping.json

# Get the mapping we just put in
curl -XGET 'http://localhost:9200/agile_data_science/_mapping/airplane'
