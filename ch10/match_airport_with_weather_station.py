# Geopy will get the distance between pairs of lat/long
import geopy

base_path = "."

#
# Load our training data and count airports
#
from pyspark.sql.types import StringType, IntegerType, FloatType, DoubleType, DateType, TimestampType
from pyspark.sql.types import StructType, StructField
from pyspark.sql.functions import udf

schema = StructType([
  StructField("ArrDelay", DoubleType(), True),  # "ArrDelay":5.0
  StructField("CRSArrTime", TimestampType(), True),  # "CRSArrTime":"2015-12-31T03:20:00.000-08:00"
  StructField("CRSDepTime", TimestampType(), True),  # "CRSDepTime":"2015-12-31T03:05:00.000-08:00"
  StructField("Carrier", StringType(), True),  # "Carrier":"WN"
  StructField("DayOfMonth", IntegerType(), True),  # "DayOfMonth":31
  StructField("DayOfWeek", IntegerType(), True),  # "DayOfWeek":4
  StructField("DayOfYear", IntegerType(), True),  # "DayOfYear":365
  StructField("DepDelay", DoubleType(), True),  # "DepDelay":14.0
  StructField("Dest", StringType(), True),  # "Dest":"SAN"
  StructField("Distance", DoubleType(), True),  # "Distance":368.0
  StructField("FlightDate", DateType(), True),  # "FlightDate":"2015-12-30T16:00:00.000-08:00"
  StructField("FlightNum", StringType(), True),  # "FlightNum":"6109"
  StructField("Origin", StringType(), True),  # "Origin":"TUS"
])

features = spark.read.json(
  "data/simple_flight_delay_features.json",
  schema=schema
)
features.registerTempTable("features")

# Get the origins and dests into one relation and count the distinct codes
from pyspark.sql.functions import col
origins = features.select(col("Origin").alias("Airport"))
dests = features.select(col("Dest").alias("Airport"))
distinct_airports = origins.union(dests).distinct()
distinct_airports.count() # 322

#
# Load and inspect the Openflights airport database
#
from pyspark.sql.types import StringType, IntegerType, DoubleType
from pyspark.sql.types import StructType, StructField

airport_schema = StructType([
  StructField("AirportID", StringType(), True),
  StructField("Name", StringType(), True),
  StructField("City", StringType(), True),
  StructField("Country", StringType(), True),
  StructField("FAA", StringType(), True),
  StructField("ICAO", StringType(), True),
  StructField("Latitude", DoubleType(), True),
  StructField("Longitude", DoubleType(), True),
  StructField("Altitude", IntegerType(), True),
  StructField("Timezone", StringType(), True),
  StructField("DST", StringType(), True),
  StructField("TimezoneOlson", StringType(), True)
])

airports = spark.read.format('com.databricks.spark.csv')\
  .options(header='false', inferschema='false')\
  .schema(airport_schema)\
  .load("data/airports.csv")

# Show ATL
airports.filter(airports.FAA == "ATL").show()
airports.count() # 8107

#
# Check out the weather stations via the WBAN Master List
#

wban_schema = StructType([
  StructField("REGION", StringType(), True),
  StructField("WBAN_ID", StringType(), True),
  StructField("STATION_NAME", StringType(), True),
  StructField("STATE_PROVINCE", StringType(), True),
  StructField("COUNTY", StringType(), True),
  StructField("COUNTRY", StringType(), True),
  StructField("EXTENDED_NAME", StringType(), True),
  StructField("CALL_SIGN", StringType(), True),
  StructField("STATION_TYPE", StringType(), True),
  StructField("DATE_ASSIGNED", StringType(), True),
  StructField("BEGIN_DATE", StringType(), True),
  StructField("COMMENTS", StringType(), True),
  StructField("LOCATION", StringType(), True),
  StructField("ELEV_OTHER", StringType(), True),
  StructField("ELEV_GROUND", StringType(), True),
  StructField("ELEV_RUNWAY", StringType(), True),
  StructField("ELEV_BAROMETRIC", StringType(), True),
  StructField("ELEV_STATION", StringType(), True),
  StructField("ELEV_UPPER_AIR", StringType(), True)
])

# Load the WBAN station master list
wban_master_list = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='false', delimiter='|')\
  .schema(wban_schema)\
  .load('data/wbanmasterlist.psv')
wban_master_list.count() # 7,411

# How many have a location?
wban_with_location = wban_master_list.filter(
  wban_master_list.LOCATION.isNotNull()
)
wban_with_location.select(
  "WBAN_ID",
  "STATION_NAME",
  "STATE_PROVINCE",
  "COUNTY",
  "COUNTRY",
  "CALL_SIGN",
  "LOCATION"
).show(10)
wban_with_location.count() # 1409

#
# Get the Latitude/Longitude of those stations with parsable locations
#
from pyspark.sql.functions import split
wban_with_lat_lon = wban_with_location.select(
  wban_with_location.WBAN_ID,
  (split(wban_with_location.LOCATION, ',')[0]).cast("float").alias("Latitude"),
  (split(wban_with_location.LOCATION, ',')[1]).cast("float").alias("Longitude")
)
wban_with_lat_lon.show(10)

# Count those that got a latitude and longitude
wban_with_lat_lon = wban_with_lat_lon.filter(
  wban_with_lat_lon.Longitude.isNotNull()
)
wban_with_lat_lon.count() # 391

#
# Extend the number of locations through geocoding
#

# Count the number of US WBANs
us_wbans = wban_master_list.filter("COUNTRY == 'US'")
us_wbans.count() # 4,601

# Compose the addresses of US WBANs
us_wban_addresses = us_wbans.selectExpr(
  "WBAN_ID",
  "CONCAT(STATION_NAME, ', ', COALESCE(COUNTY, ''), ', ', STATE_PROVINCE, ', ', COUNTRY) AS Address"
)
us_wban_addresses.show(100, False)

non_null_us_wban_addresses = us_wban_addresses.filter(
  us_wban_addresses.Address.isNotNull()
)
non_null_us_wban_addresses.count() # 4,597

# Try to geocode one record
from geopy.geocoders import Nominatim
geolocator = Nominatim()
geolocator.geocode("MARION COUNTY AIRPORT, MARION, SC, US")

# from socket import timeout
# from geopy.exc import GeocoderTimedOut
from pyspark.sql import Row

def get_location(record):
  geolocator = Nominatim()
  
  latitude = None
  longitude = None
  
  try:
    location = geolocator.geocode(record["Address"])
    if location:
      latitude = location.latitude
      longitude = location.longitude
  except:
    pass
  
  lat_lon_record = Row(
    WBAN_ID=record["WBAN_ID"],
    Latitude=latitude,
    Longitude=longitude,
    Address=record["Address"]
  )
  return lat_lon_record

# Geocode the the WBANs with addresses
wbans_geocoded = us_wban_addresses.rdd.map(get_location).toDF()

# Save the geocoded output, they take a long time to compute
geocoded_wban_output_path = "{}/data/wban_address_with_lat_lon.json".format(
  base_path
)
wbans_geocoded\
  .repartition(1)\
  .write\
  .mode("overwrite")\
  .json(geocoded_wban_output_path)

wbans_geocoded = spark.read.json(
  geocoded_wban_output_path
)

# Count the WBANs we successfully encoded
non_null_wbans_geocoded = wbans_geocoded.filter(
  wbans_geocoded.Longitude.isNotNull()
)
non_null_wbans_geocoded.show()
non_null_wbans_geocoded.count() # 1,299

# Combine the original wban_with_lat_lon with our non_null_wbans_geocoded
trimmed_geocoded_wbans = non_null_wbans_geocoded.select(
  "WBAN_ID",
  "Latitude",
  "Longitude"
)
comparable_wbans = trimmed_geocoded_wbans\
  .union(wban_with_lat_lon)\
  .distinct()
comparable_wbans.show(10)
comparable_wbans.count() # 1,692

#
# Limit the size of the airports to those in the data
#
feature_airports = airports.join(
  distinct_airports,
  on=airports.FAA == distinct_airports.Airport
)
feature_airports.count() # 322

# Only retain the essential columns
trimmed_feature_airports = feature_airports.select(
  "Airport",
  "Latitude",
  "Longitude"
)
trimmed_feature_airports.show(10)

#
# Associate weather stations with airports and compute the distance between them
#

# Do a cartesian join to pair all
airport_wban_combinations = trimmed_feature_airports.rdd.cartesian(comparable_wbans.rdd)
airport_wban_combinations.count() # 544,824

# Compute the geodesic distance between the airport and station
from geopy.distance import vincenty
def airport_station_distance(record):
  
  airport = record[0]
  station = record[1]
  
  airport_lat_lon = (airport["Latitude"], airport["Longitude"])
  station_lat_lon = (station["Latitude"], station["Longitude"])
  
  # Default to a huge distance
  distance = 24902 # equitorial circumference
  try:
    distance = round(vincenty(airport_lat_lon, station_lat_lon).miles)
  except:
    pass

  distance_record = Row(
    WBAN_ID=station["WBAN_ID"],
    StationLatitude=station["Latitude"],
    StationLongitude=station["Longitude"],
    Airport=airport["Airport"],
    AirportLatitude=airport["Latitude"],
    AirportLongitude=airport["Longitude"],
    Distance=distance,
  )
  return distance_record

# Apply calculation to our comparison pairs
distances = airport_wban_combinations.map(
  airport_station_distance
)
airport_station_distances = distances.toDF()

# Order by distance and show nearby pairs
airport_station_distances.orderBy("Distance").show()

# Store them and load them, they're expensive to calculate
distances_output_path = "{}/data/airport_station_distances.json".format(
  base_path
)

airport_station_distances\
  .write\
  .mode("overwrite")\
  .json(distances_output_path)

airport_station_distances = spark.read.json(
  distances_output_path
)

#
# Assign the closest station to each airport
#
grouped_distances = airport_station_distances.rdd.groupBy(
  lambda x: x["Airport"]
)

def get_min_distance_station(record):
  airport = record[0]
  distances = record[1]
  
  closest_station = min(distances, key=lambda x: x["Distance"])
  return Row(
    Airport=closest_station["Airport"],
    WBAN_ID=closest_station["WBAN_ID"],
    Distance=closest_station["Distance"]
  )
  
cs = grouped_distances.map(get_min_distance_station)
closest_stations = cs.toDF()

# Finally, store the pairs!
closest_stations_path = "{}/data/airport_station_pairs.json".format(
  base_path
)
closest_stations\
  .repartition(1)\
  .write\
  .mode("overwrite")\
  .json(closest_stations_path)

# Show the best and worst results
closest_stations.orderBy("Distance").show(10)
closest_stations.orderBy("Distance", ascending=False).show(10)

# Check the histogram of distances
distance_histogram = closest_stations.select("Distance")\
  .rdd\
  .flatMap(lambda x: x)\
  .histogram(
    [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 200, 500, 1100]
  )
distance_histogram
