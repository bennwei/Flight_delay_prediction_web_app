#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

# Pass date and base path to main() from airflow
def main(iso_date, base_path):

  APP_NAME = "make_predictions.py"
  
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
  
  #
  # Load each and every model in the pipeline
  #
  
  # Load the arrival delay bucketizer
  from pyspark.ml.feature import Bucketizer
  arrival_bucketizer_path = "{}/models/arrival_bucketizer_2.0.bin".format(base_path)
  arrival_bucketizer = Bucketizer.load(arrival_bucketizer_path)
  
  # Load all the string indexers into a dict
  from pyspark.ml.feature import StringIndexerModel
  
  string_indexer_models = {}
  for column in ["Carrier", "DayOfMonth", "DayOfWeek", "DayOfYear",
                 "Origin", "Dest", "Route"]:
  # for column in ["Carrier", "Origin", "Dest", "Route"]:
    string_indexer_model_path = "{}/models/string_indexer_model_{}.bin".format(
      base_path,
      column
    )
    string_indexer_model = StringIndexerModel.load(string_indexer_model_path)
    string_indexer_models[column] = string_indexer_model
  
  # Load the numeric vector assembler
  from pyspark.ml.feature import VectorAssembler
  vector_assembler_path = "{}/models/numeric_vector_assembler.bin".format(base_path)
  vector_assembler = VectorAssembler.load(vector_assembler_path)
    
  # Load the classifier model
  from pyspark.ml.classification import RandomForestClassifier, RandomForestClassificationModel
  random_forest_model_path = "{}/models/spark_random_forest_classifier.flight_delays.5.0.bin".format(
      base_path
  )
  rfc = RandomForestClassificationModel.load(
    random_forest_model_path
  )
  
  #
  # Run the requests through the transformations from training
  #
  
  # Get today and tomorrow's dates as iso strings to scope query
  today_dt = iso8601.parse_date(iso_date)
  rounded_today = today_dt.date()
  iso_today = rounded_today.isoformat()

  # Build the day's input path: a date based primary key directory structure
  today_input_path = "{}/data/prediction_tasks_daily.json/{}".format(
    base_path,
    iso_today
  )

  from pyspark.sql.types import StringType, IntegerType, DoubleType, DateType, TimestampType
  from pyspark.sql.types import StructType, StructField

  schema = StructType([
    StructField("Carrier", StringType(), True),
    StructField("DayOfMonth", IntegerType(), True),
    StructField("DayOfWeek", IntegerType(), True),
    StructField("DayOfYear", IntegerType(), True),
    StructField("DepDelay", DoubleType(), True),
    StructField("Dest", StringType(), True),
    StructField("Distance", DoubleType(), True),
    StructField("FlightDate", DateType(), True),
    StructField("FlightNum", StringType(), True),
    StructField("Origin", StringType(), True),
    StructField("Timestamp", TimestampType(), True),
  ])
  
  prediction_requests = spark.read.json(today_input_path, schema=schema)
  prediction_requests.show()

  #
  # Add a Route variable to replace FlightNum
  #
  
  from pyspark.sql.functions import lit, concat
  prediction_requests_with_route = prediction_requests.withColumn(
    'Route',
    concat(
      prediction_requests.Origin,
      lit('-'),
      prediction_requests.Dest
    )
  )
  prediction_requests_with_route.show(6)
  
  # Index string fields with the corresponding indexer for that column
  for column in ["Carrier", "DayOfMonth", "DayOfWeek", "DayOfYear",
                 "Origin", "Dest", "Route"]:
    string_indexer_model = string_indexer_models[column]
    prediction_requests_with_route = string_indexer_model.transform(prediction_requests_with_route)
      
  # Vectorize numeric columns: DepDelay and Distance
  final_vectorized_features = vector_assembler.transform(prediction_requests_with_route)
  
  # Drop the indexes for the nominal fields
  index_columns = ["Carrier_index", "DayOfMonth_index","DayOfWeek_index",
                   "DayOfYear_index", "Origin_index", "Origin_index",
                   "Dest_index", "Route_index"]
  for column in index_columns:
    final_vectorized_features = final_vectorized_features.drop(column)

  # Inspect the finalized features
  final_vectorized_features.show()
  
  # Make the prediction
  predictions = rfc.transform(final_vectorized_features)
  
  # Drop the features vector and prediction metadata to give the original fields
  predictions = predictions.drop("Features_vec")
  final_predictions = predictions.drop("indices").drop("values").drop("rawPrediction").drop("probability")
  
  # Inspect the output
  final_predictions.show()
  
  # Build the day's output path: a date based primary key directory structure
  today_output_path = "{}/data/prediction_results_daily.json/{}".format(
    base_path,
    iso_today
  )
  
  # Save the output to its daily bucket
  final_predictions.repartition(1).write.mode("overwrite").json(today_output_path)

if __name__ == "__main__":
  main(sys.argv[1], sys.argv[2])
