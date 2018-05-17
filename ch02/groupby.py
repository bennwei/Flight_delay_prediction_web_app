csv_lines = sc.textFile("data/example.csv")

# Turn the CSV lines into objects
def csv_to_record(line):
  parts = line.split(",")
  record = {
    "name": parts[0],
    "company": parts[1],
    "title": parts[2]
  }
  return record

# Apply the function to every record
records = csv_lines.map(csv_to_record)

# Inspect the first item in the dataset
records.first()

# Group the records by the name of the person
grouped_records = records.groupBy(lambda x: x["name"])

# Show the first group
grouped_records.first()

# Count the groups
job_counts = grouped_records.map(
  lambda x: {
    "name": x[0],
    "job_count": len(x[1])
  }
)

job_counts.first()

job_counts.collect()
