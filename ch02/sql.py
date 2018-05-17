csv_lines = sc.textFile("data/example.csv")

from pyspark.sql import Row

# Convert the CSV into a pyspark.sql.Row
def csv_to_row(line):
  parts = line.split(",")
  row = Row(
    name=parts[0],
    company=parts[1],
    title=parts[2]
  )
  return row

# Apply the function to get rows in an RDD
rows = csv_lines.map(csv_to_row)

# Convert to a pyspark.sql.DataFrame
rows_df = rows.toDF()

# Register the DataFrame for Spark SQL
rows_df.registerTempTable("executives")

# Generate a new DataFrame with SQL using the SparkSession
job_counts = spark.sql("""
SELECT
  name,
  COUNT(*) AS total
  FROM executives
  GROUP BY name
""")
job_counts.show()

# Go back to an RDD
job_counts.rdd.collect()
