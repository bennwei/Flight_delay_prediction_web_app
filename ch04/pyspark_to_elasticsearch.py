# Load the parquet file
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')

# Save the DataFrame to Elasticsearch
on_time_dataframe.write.format("org.elasticsearch.spark.sql")\
  .option("es.resource","agile_data_science/on_time_performance")\
  .option("es.batch.size.entries","100")\
  .mode("overwrite")\
  .save()

# Format data for Elasticsearch, as a tuple with a dummy key in the first field
# on_time_performance = on_time_dataframe.rdd.map(lambda x: ('ignored_key', x.asDict()))
#
# on_time_performance.saveAsNewAPIHadoopFile(
#   path='-',
#   outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
#   keyClass="org.apache.hadoop.io.NullWritable",
#   valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
#   conf={ "es.resource" : "agile_data_science/on_time_performance" })
