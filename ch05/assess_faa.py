# Load the FAA N-Number Inquiry Records
faa_tail_number_inquiry = spark.read.json('data/faa_tail_number_inquiry.jsonl')
faa_tail_number_inquiry.show()

# Count the records
faa_tail_number_inquiry.count()

# Load our unique tail numbers
unique_tail_numbers = spark.read.json('data/tail_numbers.jsonl')
unique_tail_numbers.show()

# left outer join tail numbers to our inquries to see how many came through
tail_num_plus_inquiry = unique_tail_numbers.join(
  faa_tail_number_inquiry,
  unique_tail_numbers.TailNum == faa_tail_number_inquiry.TailNum,
  'left_outer'
)
tail_num_plus_inquiry.show()

# Now compute the total records and the successfully joined records
total_records = tail_num_plus_inquiry.count()
join_hits = tail_num_plus_inquiry.filter(
  tail_num_plus_inquiry.owner.isNotNull()
).count()

# This being Python, we can now compute and print a join percent...
hit_ratio = float(join_hits)/float(total_records)
hit_pct = hit_ratio * 100
print("Successful joins: {:.2f}%".format(hit_pct))
