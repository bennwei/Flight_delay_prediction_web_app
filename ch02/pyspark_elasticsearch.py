csv_lines = sc.textFile("data/example.csv")
data = csv_lines.map(lambda line: line.split(","))
schema_data = data.map(lambda x: ('key', {'name': x[0], 'company': x[1], 'title': x[2]}))

schema_data.saveAsNewAPIHadoopFile(
  path='-', 
  outputFormatClass="org.elasticsearch.hadoop.mr.EsOutputFormat",
  keyClass="org.apache.hadoop.io.NullWritable", 
  valueClass="org.elasticsearch.hadoop.mr.LinkedMapWritable", 
  conf={ "es.resource" : "agile_data_science/executives" })
