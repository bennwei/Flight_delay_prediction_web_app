# Load the parquet file
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')

# Use SQL to look at the total flights by month across 2015
on_time_dataframe.registerTempTable("on_time_dataframe")
total_flights_by_month = spark.sql(
  """SELECT Month, Year, COUNT(*) AS total_flights
  FROM on_time_dataframe
  GROUP BY Year, Month
  ORDER BY Year, Month"""
)

# This map/asDict trick makes the rows print a little prettier. It is optional.
flights_chart_data = total_flights_by_month.rdd.map(lambda row: row.asDict())
flights_chart_data.collect()

# Save chart to MongoDB
import pymongo_spark
pymongo_spark.activate()
flights_chart_data.saveToMongoDB(
  'mongodb://localhost:27017/agile_data_science.flights_by_month'
)

