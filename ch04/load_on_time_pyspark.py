# Loads CSV with header parsing and type inference, in one line!
# Must use 'pyspark --packages com.databricks:spark-csv_2.10:1.4.0' for this to work
on_time_dataframe = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='true')\
  .load('data/On_Time_On_Time_Performance_2015.csv.bz2')

# Check out the data - very wide so hard to see
on_time_dataframe.show()

# Use SQL to query data - what airport pairs have the most flights?
on_time_dataframe.registerTempTable("on_time_dataframe")
airport_pair_totals = spark.sql("""SELECT
  Origin, Dest, COUNT(*) AS total
  FROM on_time_dataframe
  GROUP BY Origin, Dest
  ORDER BY total DESC"""
)

# Use dataflows
airport_pair_totals.limit(10).show()

# We can go back and forth as we see fit!

