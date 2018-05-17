#!/bin/bash

# Import our enriched airline data as the 'airlines' collection
mongoimport -d agile_data_science -c origin_dest_distances --file data/origin_dest_distances.jsonl
mongo agile_data_science --eval 'db.origin_dest_distances.ensureIndex({Origin: 1, Dest: 1})'
