import sys, os, re

# Load the on-time parquet file
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')

# The first step is easily expressed as SQL: get all unique tail numbers for each airline
on_time_dataframe.registerTempTable("on_time_performance")
carrier_codes = spark.sql(
  "SELECT DISTINCT Carrier FROM on_time_performance"
  )
carrier_codes.collect()

from pyspark.sql.types import StringType, IntegerType
from pyspark.sql.types import StructType, StructField

schema = StructType([
  StructField("ID", IntegerType(), True),  # "ArrDelay":5.0
  StructField("Name", StringType(), True),  # "CRSArrTime":"2015-12-31T03:20:00.000-08:00"
  StructField("Alias", StringType(), True),  # "CRSDepTime":"2015-12-31T03:05:00.000-08:00"
  StructField("IATA", StringType(), True),  # "Carrier":"WN"
  StructField("ICAO", StringType(), True),  # "DayOfMonth":31
  StructField("CallSign", StringType(), True),  # "DayOfWeek":4
  StructField("Country", StringType(), True),  # "DayOfYear":365
  StructField("Active", StringType(), True),  # "DepDelay":14.0
])

airlines = spark.read.format('com.databricks.spark.csv')\
  .options(header='false', nullValue='\\N')\
  .schema(schema)\
  .load('data/airlines.csv')
airlines.show()

# Is Delta around?
airlines.filter(airlines.IATA == 'DL').show()

# Drop fields except for C1 as name, C3 as carrier code
airlines.registerTempTable("airlines")
airlines = spark.sql("SELECT Name, IATA AS CarrierCode from airlines")

# Join our 14 carrier codes to the airliens table to get our set of airlines
our_airlines = carrier_codes.join(airlines, carrier_codes.Carrier == airlines.CarrierCode)
our_airlines = our_airlines.select('Name', 'CarrierCode')
our_airlines.show()

# Store as JSON objects via a dataframe. Repartition to 1 to get 1 json file.
our_airlines.repartition(1).write.mode("overwrite").json("data/our_airlines.json")

os.system("cp data/our_airlines.json/part* data/our_airlines.jsonl")

#wikidata = spark.read.json('data/wikidata-20160404-all.json.bz2')

