# Load the text file using the SparkContext
csv_lines = sc.textFile("data/example.csv")

# Map the data to split the lines into a list
data = csv_lines.map(lambda line: line.split(","))

# Collect the dataset into local RAM
data.collect()
