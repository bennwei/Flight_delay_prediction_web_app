#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

# Pass date and base path to main() from airflow
def main(iso_date, base_path):
  APP_NAME = "pyspark_task_one.py"
  
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

  # Get today's date
  today_dt = iso8601.parse_date(iso_date)
  rounded_today = today_dt.date()

  # Load today's data
  today_input_path = "{}/ch02/data/example_name_titles_daily.json/{}".format(
    base_path,
    rounded_today.isoformat()
  )

  # Otherwise load the data and proceed...
  people_titles = spark.read.json(today_input_path)
  people_titles.show()
  
  # Group by as an RDD
  titles_by_name = people_titles.rdd.groupBy(lambda x: x["name"])
  
  # Accept the group key/grouped data and concatenate the various titles...
  # into a master title
  def concatenate_titles(people_titles):
    name = people_titles[0]
    title_records = people_titles[1]
    master_title = ""
    for title_record in sorted(title_records):
      title = title_record["title"]
      master_title += "{}, ".format(title)
    master_title = master_title[:-2]
    record = {"name": name, "master_title": master_title}
    return record
  
  people_with_contactenated_titles = titles_by_name.map(concatenate_titles)
  people_output_json = people_with_contactenated_titles.map(json.dumps)
  
  # Get today's output path
  today_output_path = "{}/ch02/data/example_master_titles_daily.json/{}".format(
    base_path,
    rounded_today.isoformat()
  )
  
  # Write/replace today's output path
  os.system("rm -rf {}".format(today_output_path))
  people_output_json.saveAsTextFile(today_output_path)

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
