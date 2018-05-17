#!/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession, Row
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

# Save to Mongo
from bson import json_util
import pymongo_spark
pymongo_spark.activate()

def main(base_path):

  APP_NAME = "make_predictions_streaming.py"

  # Process data every 10 seconds
  PERIOD = 10
  BROKERS = 'localhost:9092'
  PREDICTION_TOPIC = 'flight_delay_classification_request'
  
  try:
    sc and ssc
  except NameError as e:
    import findspark

    # Add the streaming package and initialize
    findspark.add_packages(["org.apache.spark:spark-streaming-kafka-0-8_2.11:2.1.0"])
    findspark.init()
    
    import pyspark
    import pyspark.sql
    import pyspark.streaming
  
    conf = SparkConf().set("spark.default.parallelism", 1)
    sc = SparkContext(appName="Agile Data Science: PySpark Streaming 'Hello, World!'", conf=conf)
    ssc = StreamingContext(sc, PERIOD)
    spark = pyspark.sql.SparkSession(sc).builder.appName(APP_NAME).getOrCreate()
  
  #
  # Load all models to be used in making predictions
  #
  
  # Load the arrival delay bucketizer
  from pyspark.ml.feature import Bucketizer
  arrival_bucketizer_path = "{}/models/arrival_bucketizer_2.0.bin".format(base_path)
  arrival_bucketizer = Bucketizer.load(arrival_bucketizer_path)
  
  # Load all the string field vectorizer pipelines into a dict
  from pyspark.ml.feature import StringIndexerModel
  
  string_indexer_models = {}
  for column in ["Carrier", "Origin", "Dest", "Route"]:
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
  # Process Prediction Requests in Streaming
  #
  stream = KafkaUtils.createDirectStream(
    ssc,
    [PREDICTION_TOPIC],
    {
      "metadata.broker.list": BROKERS,
      "group.id": "0",
    }
  )

  object_stream = stream.map(lambda x: json.loads(x[1]))
  object_stream.pprint()
  
  row_stream = object_stream.map(
    lambda x: Row(
      FlightDate=iso8601.parse_date(x['FlightDate']),
      Origin=x['Origin'],
      Distance=x['Distance'],
      DayOfMonth=x['DayOfMonth'],
      DayOfYear=x['DayOfYear'],
      UUID=x['UUID'],
      DepDelay=x['DepDelay'],
      DayOfWeek=x['DayOfWeek'],
      FlightNum=x['FlightNum'],
      Dest=x['Dest'],
      Timestamp=iso8601.parse_date(x['Timestamp']),
      Carrier=x['Carrier']
    )
  )
  row_stream.pprint()

  #
  # Create a dataframe from the RDD-based object stream
  #

  def classify_prediction_requests(rdd):
  
    from pyspark.sql.types import StringType, IntegerType, DoubleType, DateType, TimestampType
    from pyspark.sql.types import StructType, StructField
  
    prediction_request_schema = StructType([
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
      StructField("UUID", StringType(), True),
    ])
    
    prediction_requests_df = spark.createDataFrame(rdd, schema=prediction_request_schema)
    prediction_requests_df.show()

    #
    # Add a Route variable to replace FlightNum
    #

    from pyspark.sql.functions import lit, concat
    prediction_requests_with_route = prediction_requests_df.withColumn(
      'Route',
      concat(
        prediction_requests_df.Origin,
        lit('-'),
        prediction_requests_df.Dest
      )
    )
    prediction_requests_with_route.show(6)
  
    # Vectorize string fields with the corresponding pipeline for that column
    # Turn category fields into categoric feature vectors, then drop intermediate fields
    for column in ["Carrier", "Origin", "Dest", "Route"]:
      string_indexer_model = string_indexer_models[column]
      prediction_requests_with_route = string_indexer_model.transform(prediction_requests_with_route)
  
    # Vectorize numeric columns: DepDelay, Distance and index columns
    final_vectorized_features = vector_assembler.transform(prediction_requests_with_route)
    
    # Inspect the vectors
    final_vectorized_features.show()
  
    # Drop the individual index columns
    index_columns = ["Carrier_index", "Origin_index", "Dest_index", "Route_index"]
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
  
    # Store to Mongo
    if final_predictions.count() > 0:
      final_predictions.rdd.map(lambda x: x.asDict()).saveToMongoDB(
        "mongodb://localhost:27017/agile_data_science.flight_delay_classification_response"
      )
  
  # Do the classification and store to Mongo
  row_stream.foreachRDD(classify_prediction_requests)
  
  ssc.start()
  ssc.awaitTermination()

if __name__ == "__main__":
  main(sys.argv[1])
