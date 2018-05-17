#!/usr/bin/env bash

#
# Get weather data
#

cd data

# Get the station master list as pipe-seperated-values
curl -Lko /tmp/wbanmasterlist.psv.zip http://www.ncdc.noaa.gov/homr/file/wbanmasterlist.psv.zip
unzip -o /tmp/wbanmasterlist.psv.zip
gzip wbanmasterlist.psv
rm -f /tmp/wbanmasterlist.psv.zip

# Get monthly files of daily summaries for all stations
# curl -Lko /tmp/ http://www.ncdc.noaa.gov/orders/qclcd/QCLCD201501.zip
for i in $(seq -w 1 12)
do
  curl -Lko /tmp/QCLCD2015${i}.zip http://www.ncdc.noaa.gov/orders/qclcd/QCLCD2015${i}.zip
  unzip -o /tmp/QCLCD2015${i}.zip
  gzip 2015${i}*.txt
  rm -f /tmp/QCLCD2015${i}.zip
done
