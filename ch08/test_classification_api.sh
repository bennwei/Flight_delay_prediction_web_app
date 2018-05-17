#!/usr/bin/env bash

# Fetch the delay prediction for a hypothetical flight
curl -XPOST 'http://localhost:5000/flights/delays/predict/classify' \
  -F 'DepDelay=5.0' \
  -F 'Carrier=AA' \
  -F 'FlightDate=2016-12-23' \
  -F 'Dest=ATL' \
  -F 'FlightNum=1519' \
  -F 'Origin=SFO' \
| json_pp
