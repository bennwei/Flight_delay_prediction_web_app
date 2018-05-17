# !/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

# Pass date and base path to main() from airflow
def main(base_path):
  
  APP_NAME = "train_spark_mllib_model.py"
  
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
  # {
  #   "ArrDelay":5.0,"CRSArrTime":"2015-12-31T03:20:00.000-08:00","CRSDepTime":"2015-12-31T03:05:00.000-08:00",
  #   "Carrier":"WN","DayOfMonth":31,"DayOfWeek":4,"DayOfYear":365,"DepDelay":14.0,"Dest":"SAN","Distance":368.0,
  #   "FlightDate":"2015-12-30T16:00:00.000-08:00","FlightNum":"6109","Origin":"TUS"
  # }
  #
  from pyspark.sql.types import StringType, IntegerType, FloatType, DoubleType, DateType, TimestampType
  from pyspark.sql.types import StructType, StructField
  from pyspark.sql.functions import udf
  
  schema = StructType([
    StructField("ArrDelay", DoubleType(), True),     # "ArrDelay":5.0
    StructField("CRSArrTime", TimestampType(), True),    # "CRSArrTime":"2015-12-31T03:20:00.000-08:00"
    StructField("CRSDepTime", TimestampType(), True),    # "CRSDepTime":"2015-12-31T03:05:00.000-08:00"
    StructField("Carrier", StringType(), True),     # "Carrier":"WN"
    StructField("DayOfMonth", IntegerType(), True), # "DayOfMonth":31
    StructField("DayOfWeek", IntegerType(), True),  # "DayOfWeek":4
    StructField("DayOfYear", IntegerType(), True),  # "DayOfYear":365
    StructField("DepDelay", DoubleType(), True),     # "DepDelay":14.0
    StructField("Dest", StringType(), True),        # "Dest":"SAN"
    StructField("Distance", DoubleType(), True),     # "Distance":368.0
    StructField("FlightDate", DateType(), True),    # "FlightDate":"2015-12-30T16:00:00.000-08:00"
    StructField("FlightNum", StringType(), True),   # "FlightNum":"6109"
    StructField("Origin", StringType(), True),      # "Origin":"TUS"
  ])
  
  input_path = "{}/data/simple_flight_delay_features.json".format(
    base_path
  )
  features = spark.read.json(input_path, schema=schema)
  features.first()
  
  #
  # Check for nulls in features before using Spark ML
  #
  null_counts = [(column, features.where(features[column].isNull()).count()) for column in features.columns]
  cols_with_nulls = filter(lambda x: x[1] > 0, null_counts)
  print(list(cols_with_nulls))
  
  #
  # Add a Route variable to replace FlightNum
  #
  from pyspark.sql.functions import lit, concat
  features_with_route = features.withColumn(
    'Route',
    concat(
      features.Origin,
      lit('-'),
      features.Dest
    )
  )
  features_with_route.show(6)
  
  #
  # Use pysmark.ml.feature.Bucketizer to bucketize ArrDelay into on-time, slightly late, very late (0, 1, 2)
  #
  from pyspark.ml.feature import Bucketizer

  # Setup the Bucketizer
  splits = [-float("inf"), -15.0, 0, 30.0, float("inf")]
  arrival_bucketizer = Bucketizer(
    splits=splits,
    inputCol="ArrDelay",
    outputCol="ArrDelayBucket"
  )

  # Save the model
  arrival_bucketizer_path = "{}/models/arrival_bucketizer_2.0.bin".format(base_path)
  arrival_bucketizer.write().overwrite().save(arrival_bucketizer_path)
  
  # Apply the model
  ml_bucketized_features = arrival_bucketizer.transform(features_with_route)
  ml_bucketized_features.select("ArrDelay", "ArrDelayBucket").show()
  
  #
  # Extract features tools in with pyspark.ml.feature
  #
  from pyspark.ml.feature import StringIndexer, VectorAssembler
  
  # Turn category fields into indexes
  for column in ["Carrier", "DayOfMonth", "DayOfWeek", "DayOfYear",
                 "Origin", "Dest", "Route"]:
    string_indexer = StringIndexer(
      inputCol=column,
      outputCol=column + "_index"
    )
    
    string_indexer_model = string_indexer.fit(ml_bucketized_features)
    ml_bucketized_features = string_indexer_model.transform(ml_bucketized_features)
    
    # Drop the original column
    ml_bucketized_features = ml_bucketized_features.drop(column)
    
    # Save the pipeline model
    string_indexer_output_path = "{}/models/string_indexer_model_{}.bin".format(
      base_path,
      column
    )
    string_indexer_model.write().overwrite().save(string_indexer_output_path)
  
  # Handle continuous, numeric fields by combining them into one feature vector
  numeric_columns = ["DepDelay", "Distance"]
  index_columns = ["Carrier_index", "DayOfMonth_index",
                   "DayOfWeek_index", "DayOfYear_index", "Origin_index",
                   "Origin_index", "Dest_index", "Route_index"]
  vector_assembler = VectorAssembler(
    inputCols=numeric_columns + index_columns,
    outputCol="Features_vec"
  )
  final_vectorized_features = vector_assembler.transform(ml_bucketized_features)

  # Save the numeric vector assembler
  vector_assembler_path = "{}/models/numeric_vector_assembler.bin".format(base_path)
  vector_assembler.write().overwrite().save(vector_assembler_path)
  
  # Drop the index columns
  for column in index_columns:
    final_vectorized_features = final_vectorized_features.drop(column)
  
  # Inspect the finalized features
  final_vectorized_features.show()
  
  #
  # Cross validate, train and evaluate classifier: loop 5 times for 4 metrics
  #

  from collections import defaultdict
  scores = defaultdict(list)
  metric_names = ["accuracy", "weightedPrecision", "weightedRecall", "f1"]
  split_count = 3

  for i in range(1, split_count + 1):
    print("Run {} out of {} of test/train splits in cross validation...".format(
        i,
        split_count,
      )
    )
  
    # Test/train split
    training_data, test_data = final_vectorized_features.randomSplit([0.8, 0.2])
  
    # Instantiate and fit random forest classifier on all the data
    from pyspark.ml.classification import RandomForestClassifier
    rfc = RandomForestClassifier(
      featuresCol="Features_vec",
      labelCol="ArrDelayBucket",
      predictionCol="Prediction",
      maxBins=4657,
    )
    model = rfc.fit(training_data)
  
    # Save the new model over the old one
    model_output_path = "{}/models/spark_random_forest_classifier.flight_delays.baseline.bin".format(
      base_path
    )
    model.write().overwrite().save(model_output_path)
  
    # Evaluate model using test data
    predictions = model.transform(test_data)
    
    # Evaluate this split's results for each metric
    from pyspark.ml.evaluation import MulticlassClassificationEvaluator
    for metric_name in metric_names:
      
      evaluator = MulticlassClassificationEvaluator(
        labelCol="ArrDelayBucket",
        predictionCol="Prediction",
        metricName=metric_name
      )
      score = evaluator.evaluate(predictions)

      scores[metric_name].append(score)
      print("{} = {}".format(metric_name, score))

  #
  # Evaluate average and STD of each metric
  #
  import numpy as np
  for metric_name in metric_names:
    metric_scores = scores[metric_name]
    
    average_accuracy = sum(metric_scores) / len(metric_scores)
    print("AVG {} = {:.3f}".format(metric_name, average_accuracy))
  
    std_accuracy = np.std(metric_scores)
    print("STD {} = {:.3f}".format(metric_name, std_accuracy))

  #
  # Evaluate average and STD of each metric
  #
  import numpy as np
  score_averages = defaultdict(float)

  for metric_name in metric_names:
    metric_scores = scores[metric_name]
  
    average_accuracy = sum(metric_scores) / len(metric_scores)
    print("AVG {} = {:.4f}".format(metric_name, average_accuracy))
    score_averages[metric_name] = average_accuracy
  
    std_accuracy = np.std(metric_scores)
    print("STD {} = {:.4f}".format(metric_name, std_accuracy))

  #
  # Persist the score to a sccore log that exists between runs
  #
  import pickle

  # Load the score log or initialize an empty one
  try:
    score_log_filename = "{}/models/score_log.pickle".format(base_path)
    score_log = pickle.load(open(score_log_filename, "rb"))
    if not isinstance(score_log, list):
      score_log = []
  except IOError:
    score_log = []

  # Compute the existing score log entry
  score_log_entry = {metric_name: score_averages[metric_name] for metric_name in metric_names}

  # Compute and display the change in score for each metric
  try:
    last_log = score_log[-1]
  except (IndexError, TypeError, AttributeError):
    last_log = score_log_entry

  for metric_name in metric_names:
    run_delta = score_log_entry[metric_name] - last_log[metric_name]
    print("{} delta: {:.4f}".format(metric_name, run_delta))

  # Append the existing average scores to the log
  score_log.append(score_log_entry)

  # Persist the log for next run
  pickle.dump(score_log, open(score_log_filename, "wb"))

if __name__ == "__main__":
  main(sys.argv[1])
