# Load the parquet file containing flight delay records
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')

# Register the data for Spark SQL
on_time_dataframe.registerTempTable("on_time_performance")

# Check out the columns
on_time_dataframe.columns

# Check out some data
on_time_dataframe\
  .select("FlightDate", "TailNum", "Origin", "Dest", "Carrier", "DepDelay", "ArrDelay")\
  .show()

# Trim the fields and keep the result
trimmed_on_time = on_time_dataframe\
  .select(
    "FlightDate",
    "TailNum",
    "Origin",
    "Dest",
    "Carrier",
    "DepDelay",
    "ArrDelay"
  )

# Sample 0.01% of the data and show
trimmed_on_time.sample(False, 0.0001).show()
