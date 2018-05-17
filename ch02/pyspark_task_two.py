#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

# Pass date and base path to main() from airflow
def main(iso_date, base_path):
  APP_NAME = "pyspark_task_two.py"
  
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

  import pymongo
  import pymongo_spark
  # Important: activate pymongo_spark.
  pymongo_spark.activate()
  
  # Get today's date
  today_dt = iso8601.parse_date(iso_date)
  rounded_today = today_dt.date()
  
  # Load today's data
  today_input_path = "{}/ch02/data/example_master_titles_daily.json/{}".format(
    base_path,
    rounded_today.isoformat()
  )
  
  # Otherwise load the data and proceed...
  people_master_titles_raw = sc.textFile(today_input_path)
  people_master_titles = people_master_titles_raw.map(json.loads)
  print(people_master_titles.first())

  people_master_titles.saveToMongoDB('mongodb://localhost:27017/agile_data_science.people_master_titles')

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
