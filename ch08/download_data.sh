#!/usr/bin/env bash

# Get the absolute path of this script, see http://bit.ly/find_path
ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")"
ABSOLUTE_DIR=$(dirname "${ABSOLUTE_PATH}")

# Extract to Agile_Data_Code_2/data/on_time_performance.parquet, wherever we are executed from
cd $ABSOLUTE_DIR/../data/
curl -Lko ./simple_flight_delay_features.jsonl.bz2 http://s3.amazonaws.com/agile_data_science/simple_flight_delay_features.jsonl.bz2

# Get the distances between pairs of airports
curl -Lko ./origin_dest_distances.jsonl http://s3.amazonaws.com/agile_data_science/origin_dest_distances.jsonl

# Get the models to make ch08/web/predict_flask.py go
cd $ABSOLUTE_DIR/..
mkdir models
curl -Lko ./models/sklearn_vectorizer.pkl http://s3.amazonaws.com/agile_data_science/sklearn_vectorizer.pkl
curl -Lko ./models/sklearn_regressor.pkl http://s3.amazonaws.com/agile_data_science/sklearn_regressor.pkl
