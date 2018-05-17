#!/usr/bin/env bash

curl -Lko data/on_time_performance.parquet.tgz https://s3.amazonaws.com/agile_data_science/on_time_performance.parquet.tgz
tar -xvzf data/on_time_performance.parquet.tgz -C data
