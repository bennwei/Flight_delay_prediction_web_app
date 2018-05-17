# Load our airplanes
airplanes = spark.read.json("data/airplanes.json")
airplanes.show()

airplanes.write.format("org.elasticsearch.spark.sql")\
  .option("es.resource","agile_data_science/airplane")\
  .mode("overwrite")\
  .save()

# Format data for Elasticsearch, as a tuple with a dummy key in the first field
# airplanes_dict = airplanes.rdd.map(lambda x: ('ignored_key', x.asDict()))
#
# airplanes_dict.saveAsNewAPIHadoopFile(
#   path='-',
#   outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
#   keyClass="org.apache.hadoop.io.NullWritable",
#   valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable",
#   conf={ "es.resource" : "agile_data_science/airplanes" })
