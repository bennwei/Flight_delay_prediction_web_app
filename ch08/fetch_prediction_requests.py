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
  
  APP_NAME = "fetch_prediction_requests.py"
  
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
  rounded_tomorrow_dt = rounded_today + datetime.timedelta(days=1)
  iso_tomorrow = rounded_tomorrow_dt.isoformat()
  
  # Create mongo query string for today's data
  mongo_query_string = """{{
    "Timestamp": {{
      "$gte": "{iso_today}",
      "$lte": "{iso_tomorrow}"
    }}
  }}""".format(
    iso_today=iso_today,
    iso_tomorrow=iso_tomorrow
  )
  mongo_query_string = mongo_query_string.replace('\n', '')
  
  # Create the config object with the query string
  mongo_query_config = dict()
  mongo_query_config["mongo.input.query"] = mongo_query_string
  
  # Load the day's requests using pymongo_spark
  prediction_requests = sc.mongoRDD(
    'mongodb://localhost:27017/agile_data_science.prediction_tasks',
    config=mongo_query_config
  )
  
  # Build the day's output path: a date based primary key directory structure
  today_output_path = "{}/data/prediction_tasks_daily.json/{}".format(
    base_path,
    iso_today
  )
  
  # Generate json records
  prediction_requests_json = prediction_requests.map(json_util.dumps)
  
  # Write/replace today's output path
  os.system("rm -rf {}".format(today_output_path))
  prediction_requests_json.saveAsTextFile(today_output_path)

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
