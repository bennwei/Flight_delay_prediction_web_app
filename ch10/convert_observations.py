#
# Convert hourly weather PSV to Parquet format for improved performance
#

from pyspark.sql.types import StringType, IntegerType, DoubleType
from pyspark.sql.types import StructType, StructField

hourly_schema = StructType([
  StructField("WBAN", StringType(), True),
  StructField("Date", StringType(), True),
  StructField("Time", StringType(), True),
  StructField("StationType", StringType(), True),
  StructField("SkyCondition", StringType(), True),
  StructField("SkyConditionFlag", StringType(), True),
  StructField("Visibility", StringType(), True),
  StructField("VisibilityFlag", StringType(), True),
  StructField("WeatherType", StringType(), True),
  StructField("WeatherTypeFlag", StringType(), True),
  StructField("DryBulbFarenheit", StringType(), True),
  StructField("DryBulbFarenheitFlag", StringType(), True),
  StructField("DryBulbCelsius", StringType(), True),
  StructField("DryBulbCelsiusFlag", StringType(), True),
  StructField("WetBulbFarenheit", StringType(), True),
  StructField("WetBulbFarenheitFlag", StringType(), True),
  StructField("WetBulbCelsius", StringType(), True),
  StructField("WetBulbCelsiusFlag", StringType(), True),
  StructField("DewPointFarenheit", StringType(), True),
  StructField("DewPointFarenheitFlag", StringType(), True),
  StructField("DewPointCelsius", StringType(), True),
  StructField("DewPointCelsiusFlag", StringType(), True),
  StructField("RelativeHumidity", StringType(), True),
  StructField("RelativeHumidityFlag", StringType(), True),
  StructField("WindSpeed", StringType(), True),
  StructField("WindSpeedFlag", StringType(), True),
  StructField("WindDirection", StringType(), True),
  StructField("WindDirectionFlag", StringType(), True),
  StructField("ValueForWindCharacter", StringType(), True),
  StructField("ValueForWindCharacterFlag", StringType(), True),
  StructField("StationPressure", StringType(), True),
  StructField("StationPressureFlag", StringType(), True),
  StructField("PressureTendency", StringType(), True),
  StructField("PressureTendencyFlag", StringType(), True),
  StructField("PressureChange", StringType(), True),
  StructField("PressureChangeFlag", StringType(), True),
  StructField("SeaLevelPressure", StringType(), True),
  StructField("SeaLevelPressureFlag", StringType(), True),
  StructField("RecordType", StringType(), True),
  StructField("RecordTypeFlag", StringType(), True),
  StructField("HourlyPrecip", StringType(), True),
  StructField("HourlyPrecipFlag", StringType(), True),
  StructField("Altimeter", StringType(), True),
  StructField("AltimeterFlag", StringType(), True),
])

# Load the weather records themselves
hourly_weather_records = spark.read.format('com.databricks.spark.csv')\
  .options(header='true', inferschema='false', delimiter=',')\
  .schema(hourly_schema)\
  .load('data/2015*hourly.txt.gz')
hourly_weather_records.show()

hourly_columns = ["WBAN", "Date", "Time", "SkyCondition",
                  "Visibility", "WeatherType", "DryBulbCelsius",
                  "WetBulbCelsius", "DewPointCelsius",
                  "RelativeHumidity", "WindSpeed", "WindDirection",
                  "ValueForWindCharacter", "StationPressure",
                  "SeaLevelPressure", "HourlyPrecip", "Altimeter"]

trimmed_hourly_records = hourly_weather_records.select(hourly_columns)
trimmed_hourly_records.show()

#
# Add an ISO8601 formatted ISODate column using DataFrame udfs
#
from pyspark.sql.functions import udf

# Convert station date to ISO Date
def station_date_to_iso(station_date):
  str_date = str(station_date)
  year = str_date[0:4]
  month = str_date[4:6]
  day = str_date[6:8]
  return "{}-{}-{}".format(year, month, day)

extract_date_udf = udf(station_date_to_iso, StringType())
hourly_weather_with_iso_date = trimmed_hourly_records.withColumn(
  "ISODate",
  extract_date_udf(trimmed_hourly_records.Date)
)

# Convert station time to ISO time
def station_time_to_iso(station_time):
  hour = station_time[0:2]
  minute = station_time[2:4]
  iso_time = "{hour}:{minute}:00".format(
    hour=hour,
    minute=minute
  )
  return iso_time

extract_time_udf = udf(station_time_to_iso, StringType())
hourly_weather_with_iso_time = hourly_weather_with_iso_date.withColumn(
  "ISOTime",
  extract_time_udf(trimmed_hourly_records.Time)
)

from pyspark.sql.functions import concat, lit
hourly_weather_with_iso_datetime = hourly_weather_with_iso_time.withColumn(
  "Datetime",
  concat(
    hourly_weather_with_iso_time.ISODate,
    lit("T"),
    hourly_weather_with_iso_time.ISOTime
  )
)

#
# Trim the final records, lose the original Date/Time fields and save
#
from pyspark.sql.functions import col
final_hourly_columns = ["WBAN", col("ISODate").alias("Date"), "Datetime", "SkyCondition",
                        "Visibility", "WeatherType", "DryBulbCelsius",
                        "WetBulbCelsius", "DewPointCelsius",
                        "RelativeHumidity", "WindSpeed", "WindDirection",
                        "ValueForWindCharacter", "StationPressure",
                        "SeaLevelPressure", "HourlyPrecip", "Altimeter"]
final_trimmed_hourly_records = hourly_weather_with_iso_datetime.select(
  final_hourly_columns
)
final_trimmed_hourly_records.show(5)

# Save cleaned up records using Parquet for improved performance
final_trimmed_hourly_records\
  .write\
  .mode("overwrite")\
  .parquet("data/2015_hourly_observations.parquet")
