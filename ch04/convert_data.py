from pyspark.sql import

# Loads CSV with header parsing and type inference, in one line!
on_time_dataframe = spark.read.format('com.databricks.spark.csv')\
  .options(
    header='true',
    treatEmptyValuesAsNulls='true',
  )\
  .load('data/On_Time_On_Time_Performance_2015.csv.bz2')
on_time_dataframe.registerTempTable("on_time_performance")

trimmed_cast_performance = spark.sql("""
SELECT
  Year, Quarter, Month, DayofMonth, DayOfWeek, FlightDate,
  Carrier, TailNum, FlightNum,
  Origin, OriginCityName, OriginState,
  Dest, DestCityName, DestState,
  DepTime, cast(DepDelay as float), cast(DepDelayMinutes as int),
  cast(TaxiOut as float), cast(TaxiIn as float),
  WheelsOff, WheelsOn,
  ArrTime, cast(ArrDelay as float), cast(ArrDelayMinutes as float),
  cast(Cancelled as int), cast(Diverted as int),
  cast(ActualElapsedTime as float), cast(AirTime as float),
  cast(Flights as int), cast(Distance as float),
  cast(CarrierDelay as float), cast(WeatherDelay as float), cast(NASDelay as float),
  cast(SecurityDelay as float), cast(LateAircraftDelay as float),
  CRSDepTime, CRSArrTime
FROM
  on_time_performance
""")

# Replace on_time_performance table with our new, trimmed table and show its contents
trimmed_cast_performance.registerTempTable("on_time_performance")
trimmed_cast_performance.show()

# Verify we can sum numeric columns
spark.sql("""SELECT
  SUM(WeatherDelay), SUM(CarrierDelay), SUM(NASDelay),
  SUM(SecurityDelay), SUM(LateAircraftDelay)
FROM on_time_performance
""").show()

# Save records as gzipped json lines
trimmed_cast_performance.toJSON()\
  .saveAsTextFile(
    'data/on_time_performance.jsonl.gz',
    'org.apache.hadoop.io.compress.GzipCodec'
  )

# View records on filesystem
# gunzip -c data/on_time_performance.jsonl.gz/part-00000.gz | head

# Save records using Parquet
trimmed_cast_performance.write.mode("overwrite").parquet("data/on_time_performance.parquet")

# Load JSON records back
on_time_dataframe = spark.read.json('data/on_time_performance.jsonl.gz')
on_time_dataframe.show()

# Load the parquet file back
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')
on_time_dataframe.show()
