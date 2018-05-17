csv_lines = sc.textFile("data/example.csv")

# Compute a relation of words by line
words_by_line = csv_lines\
  .map(lambda line: line.split(","))

words_by_line.collect()

# Compute a relation of words
flattened_words = csv_lines\
  .map(lambda line: line.split(","))\
  .flatMap(lambda x: x)

flattened_words.collect()
