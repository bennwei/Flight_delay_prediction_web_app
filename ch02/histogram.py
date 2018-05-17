# Load the parquet file containing flight delay records
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')

# Register the data for Spark SQL
on_time_dataframe.registerTempTable("on_time_performance")

# Compute a histogram of departure delays
on_time_dataframe\
  .select("DepDelay")\
  .rdd\
  .flatMap(lambda x: x)\
  .histogram(10)

import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt

# Function to plot a histogram using pyplot
def create_hist(rdd_histogram_data):
  """Given an RDD.histogram, plot a pyplot histogram"""
  heights = np.array(rdd_histogram_data[1])
  full_bins = rdd_histogram_data[0]
  mid_point_bins = full_bins[:-1]
  widths = [abs(i - j) for i, j in zip(full_bins[:-1], full_bins[1:])]
  bar = plt.bar(mid_point_bins, heights, width=widths, color='b')
  return bar

# Compute a histogram of departure delays
departure_delay_histogram = on_time_dataframe\
  .select("DepDelay")\
  .rdd\
  .flatMap(lambda x: x)\
  .histogram(10, [-60,-30,-15,-10,-5,0,5,10,15,30,60,90,120,180])

create_hist(departure_delay_histogram)
