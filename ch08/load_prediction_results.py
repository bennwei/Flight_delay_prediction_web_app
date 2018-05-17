#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

# Save to Mongo
from bson import json_util
import pymongo_spark
pymongo_spark.activate()

# Pass date and base path to main() from airflow
def main(iso_date, base_path):
  
  APP_NAME = "load_prediction_results.py"
  
  # If there is no SparkSession, create the environment
  try:
    sc and spark
  except NameError as e:
    import findspark
    findspark.init()
    import pyspark
    import pyspark.sql
    
    sc = pyspark.SparkContext()
    spark = pyspark.sql.SparkSession(sc).builder.appName(APP_NAME).getOrCreate()
  
  # Get today and tomorrow's dates as iso strings to scope query
  today_dt = iso8601.parse_date(iso_date)
  rounded_today = today_dt.date()
  iso_today = rounded_today.isoformat()
  
  input_path = "{}/data/prediction_results_daily.json/{}".format(
    base_path,
    iso_today
  )
  
  # Load and JSONize text
  prediction_results_raw = sc.textFile(input_path)
  prediction_results = prediction_results_raw.map(json_util.loads)
  
  # Store to MongoDB
  prediction_results.saveToMongoDB(
    "mongodb://localhost:27017/agile_data_science.prediction_results"
  )

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
