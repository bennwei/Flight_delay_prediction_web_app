# !/usr/bin/env python

import sys, os, re
import json
import datetime, iso8601

base_path = "."

from pyspark.sql.types import StringType, IntegerType, FloatType, DoubleType, DateType, TimestampType
from pyspark.sql.types import StructType, StructField
from pyspark.sql.functions import udf

schema = StructType([
  StructField("ArrDelay", DoubleType(), True),  # "ArrDelay":5.0
  StructField("CRSArrTime", TimestampType(), True),  # "CRSArrTime":"2015-12-31T03:20:00.000-08:00"
  StructField("CRSDepTime", TimestampType(), True),  # "CRSDepTime":"2015-12-31T03:05:00.000-08:00"
  StructField("Carrier", StringType(), True),  # "Carrier":"WN"
  StructField("DayOfMonth", IntegerType(), True),  # "DayOfMonth":31
  StructField("DayOfWeek", IntegerType(), True),  # "DayOfWeek":4
  StructField("DayOfYear", IntegerType(), True),  # "DayOfYear":365
  StructField("DepDelay", DoubleType(), True),  # "DepDelay":14.0
  StructField("Dest", StringType(), True),  # "Dest":"SAN"
  StructField("Distance", DoubleType(), True),  # "Distance":368.0
  StructField("FlightDate", DateType(), True),  # "FlightDate":"2015-12-30T16:00:00.000-08:00"
  StructField("FlightNum", StringType(), True),  # "FlightNum":"6109"
  StructField("Origin", StringType(), True),  # "Origin":"TUS"
])

features = spark.read.json(
  "data/simple_flight_delay_features.json",
  schema=schema
)
features.registerTempTable("features")
features.show()

#
# Check whether lateness varies a lot by hour scheduled departure/arrival
#

spark.sql("""
  SELECT
    HOUR(CRSDepTime) + 1 AS Hour,
    AVG(ArrDelay),
    STD(ArrDelay)
  FROM features
  GROUP BY HOUR(CRSDepTime)
  ORDER BY HOUR(CRSDepTime)
""").show(24)

spark.sql("""
  SELECT
    HOUR(CRSArrTime) + 1 AS Hour,
    AVG(ArrDelay),
    STD(ArrDelay)
  FROM features
  GROUP BY HOUR(CRSArrTime)
  ORDER BY HOUR(CRSArrTime)
""").show(24)
