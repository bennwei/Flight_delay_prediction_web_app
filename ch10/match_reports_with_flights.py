base_path = "."

# Load the on-time parquet file
on_time_dataframe = spark.read.parquet('data/on_time_performance.parquet')
on_time_dataframe = on_time_dataframe.limit(100000)
on_time_dataframe.registerTempTable("on_time_performance")

# Load airport/station mappings
closest_stations_path = "{}/data/airport_station_pairs.json".format(
  base_path
)
closest_stations = spark.read.json(closest_stations_path)

import json
from pyspark.sql.types import StringType
from pyspark.sql.functions import col, udf, lit, concat

# Convert station time to ISO time
def crs_time_to_iso(station_time):
  hour = station_time[0:2]
  minute = station_time[2:4]
  if int(hour) == 24:
    hour = "23"
    minute = "59"
  iso_time = "{hour}:{minute}:00".format(
    hour=hour,
    minute=minute
  )
  return iso_time

extract_time_udf = udf(crs_time_to_iso, StringType())

trimmed_flights = on_time_dataframe.select(
  "FlightNum",
  concat("FlightDate", lit("T"), extract_time_udf("CRSDepTime")).alias("CRSDepDatetime"),
  concat("FlightDate", lit("T"), extract_time_udf("CRSArrTime")).alias("CRSArrDatetime"),
  "FlightDate",
  "Origin",
  "Dest",
)

import iso8601
from datetime import timedelta
def increment_arrival_date(departure, arrival):
  """Handle overnight flights by incrementing the arrival date if a flight arrives earlier than it leaves"""
  d_dt = iso8601.parse_date(departure)
  a_dt = iso8601.parse_date(arrival)
  if a_dt.time() < d_dt.time():
    a_dt = a_dt + timedelta(days=1)
  return a_dt.isoformat()

increment_arrival_udf = udf(increment_arrival_date, StringType())

fixed_trimmed_flights = trimmed_flights.select(
  "FlightNum",
  "CRSDepDatetime",
  increment_arrival_udf("CRSDepDatetime", "CRSArrDatetime").alias("CRSArrDatetime"),
  "FlightDate",
  "Origin",
  "Dest"
)

# Join and get the origin WBAN ID
flights_with_origin_station = fixed_trimmed_flights.join(
  closest_stations,
  trimmed_flights.Origin == closest_stations.Airport
)
flights_with_origin_station = flights_with_origin_station.select(
  "FlightNum",
  "CRSDepDatetime",
  "CRSArrDatetime",
  "FlightDate",
  "Origin",
  "Dest",
  col("WBAN_ID").alias("Origin_WBAN_ID")
)

# Join and get the destination WBAN ID
flights_with_dest_station = flights_with_origin_station.join(
  closest_stations,
  flights_with_origin_station.Dest == closest_stations.Airport
)
flights_with_both_stations = flights_with_dest_station.select(
  "FlightNum",
  "CRSDepDatetime",
  "CRSArrDatetime",
  "FlightDate",
  "Origin",
  "Dest",
  "Origin_WBAN_ID",
  col("WBAN_ID").alias("Dest_WBAN_ID")
)

# Prepare for join on with that day's station's observations
from frozendict import frozendict
joinable_departure = flights_with_both_stations\
  .rdd\
  .repartition(1)\
  .map(
    lambda row: (
      frozendict({
        'WBAN': row.Origin_WBAN_ID,  # compound key
        'Date': iso8601.parse_date(row.CRSDepDatetime).date().isoformat(),
      }),
      row
    )
  )

# Daily observation groupings
daily_station_observations_raw = sc.textFile("data/daily_station_observations.json")
daily_station_observations = daily_station_observations_raw.map(json.loads)

# Prepare for RDD join
def make_observations_joinable(daily_observations):
  return (
    frozendict({
      "Date": daily_observations["Date"],
      "WBAN": daily_observations["WBAN"],
    }),
    daily_observations
  )
joinable_observations = daily_station_observations.map(make_observations_joinable)

# Do the join, store and load to/from disk
flights_with_observations = joinable_departure.join(joinable_observations)
#flights_with_observations.map(json.dumps).saveAsTextFile("data/flights_with_observations.json")
#flights_with_observations = sc.textFile("data/flights_with_observations.json").map(json.loads)

from pyspark.sql import Row
# Unwrap the join, find the nearest observation to our flight from the list for that day
def find_closest_observation(flight_with_observations, input_key, output_key):
  key = flight_with_observations[0]
  record = flight_with_observations[1]
  flight_record = record[0]
  observation_record = record[1]
  
  flight_departure_time = flight_record[input_key]
  flight_dt = iso8601.parse_date(flight_departure_time)
  
  observations = observation_record["Observations"]
  
  closest_observation = None
  closest_diff = timedelta(days=30)
  for observation in observations:
    observation_dt = iso8601.parse_date(observation["Datetime"])
    diff = flight_dt - observation_dt
    if diff < closest_diff:
      closest_observation = observation
      closest_diff = diff
  
  # Now emit final record
  if isinstance(flight_record, Row):
    new_record = flight_record.asDict()
  else:
    new_record = flight_record
  new_record[output_key] = closest_observation
  return new_record

flight_with_closest_dep_observation = flights_with_observations\
  .map(
    lambda x: find_closest_observation(x, "CRSDepDatetime", "DepObservation")
  )

# Now repeat for the scheduled arrival observation
joinable_arrivals = flight_with_closest_dep_observation\
  .map(
    lambda row: (
      frozendict({
        'WBAN': row["Dest_WBAN_ID"],  # compound key
        'Date': iso8601.parse_date(row["CRSArrDatetime"]).date().isoformat(),
      }),
      row
    )
  )
flights_with_both_observations = joinable_arrivals.join(joinable_observations)
final_observations = flights_with_both_observations\
  .map(
    lambda x: find_closest_observation(x, "CRSArrDatetime", "ArrObservation")
  )

