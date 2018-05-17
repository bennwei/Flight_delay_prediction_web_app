#!/bin/bash

# Import our enriched airline data as the 'airlines' collection
mongoimport -d agile_data_science -c airlines --file data/our_airlines_with_wiki.jsonl
