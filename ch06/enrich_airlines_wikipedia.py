import sys, os, re
sys.path.append("/lib")
from lib import utils

import wikipedia
from bs4 import BeautifulSoup
import tldextract

# Load our airlines...
our_airlines = utils.read_json_lines_file('our_airlines.jsonl')

# Build a new list that includes wikipedia data
with_url = []
for airline in our_airlines:
  # Get the wikipedia page for the airline name
  wikipage = wikipedia.page(airline['Name'])

  # Get the summary
  summary = wikipage.summary
  airline['summary'] = summary

  # Get the HTML of the page
  page = BeautifulSoup(wikipage.html())

  # Task: get the logo from the right 'vcard' column
  # 1) Get the vcard table
  vcard_table = page.find_all('table', class_='vcard')[0]
  # 2) The logo is always the first image inside this table
  first_image = vcard_table.find_all('img')[0]
  # 3) Set the url to the image
  logo_url = 'http:' + first_image.get('src')
  airline['logo_url'] = logo_url

  # Task: Get the company website
  # 1) Find the 'Website' table header
  th = page.find_all('th', text='Website')[0]
  # 2) find the parent tr element
  tr = th.parent
  # 3) find the a (link) tag within the tr
  a = tr.find_all('a')[0]
  # 4) finally get the href of the a tag
  url = a.get('href')
  airline['url'] = url

  # Get the domain to display with the url
  url_parts = tldextract.extract(url)
  airline['domain'] = url_parts.domain + '.' + url_parts.suffix

  with_url.append(airline)

utils.write_json_lines_file(with_url, 'our_airlines_with_wiki.jsonl')

