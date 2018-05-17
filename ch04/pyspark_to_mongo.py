import pymongo
import pymongo_spark
# Important: activate pymongo_spark.
pymongo_spark.activate()

on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')

# Note we have to convert the row to a dict to avoid https://jira.mongodb.org/browse/HADOOP-276
as_dict = on_time_dataframe.rdd.map(lambda row: row.asDict())
as_dict.saveToMongoDB('mongodb://localhost:27017/agile_data_science.on_time_performance')
