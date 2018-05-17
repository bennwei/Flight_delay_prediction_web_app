import sys, os, re
import time

sys.path.append("lib")
import utils

import requests
from bs4 import BeautifulSoup

tail_number_records = utils.read_json_lines_file('data/tail_numbers.jsonl')

aircraft_records = []
# Loop through the tail numbers, fetching
for tail_number_record in tail_number_records:
  time.sleep(0.1) # essential to sleep FIRST in loop or you will flood sites
  
  # Parameterize the URL with the tail number
  BASE_URL = 'http://registry.faa.gov/aircraftinquiry/NNum_Results.aspx?NNumbertxt={}'
  tail_number = tail_number_record['TailNum']
  url = BASE_URL.format(tail_number)

  # Fetch the page, parse the HTML
  r = requests.get(url)
  
  html = r.text
  soup = BeautifulSoup(html)
  
  # The table structure is constant for all pages that contain data
  try:
    aircraft_description = soup.find_all('table')[4]
    craft_tds = aircraft_description.find_all('td')
    serial_number = craft_tds[1].text.strip()
    manufacturer = craft_tds[5].text.strip()
    model = craft_tds[9].text.strip()
    mfr_year = craft_tds[25].text.strip()

    registered_owner = soup.find_all('table')[5]
    reg_tds = registered_owner.find_all('td')
    owner = reg_tds[1].text.strip()
    owner_state = reg_tds[9].text.strip()

    airworthiness = soup.find_all('table')[6]
    worthy_tds = airworthiness.find_all('td')
    engine_manufacturer = worthy_tds[1].text.strip()
    engine_model = worthy_tds[5].text.strip()

    aircraft_record = {
      'TailNum': tail_number,
      'serial_number': serial_number,
      'manufacturer': manufacturer,
      'model': model,
      'mfr_year': mfr_year,
      'owner': owner,
      'owner_state': owner_state,
      'engine_manufacturer': engine_manufacturer,
      'engine_model': engine_model,
    }
    aircraft_records.append(
      aircraft_record
    )
    print(aircraft_record)
    
  except IndexError as e:
    print("Missing {} record: {}".format(tail_number, e))

utils.write_json_lines_file(
  aircraft_records, 'data/faa_tail_number_inquiry.jsonl'
)
