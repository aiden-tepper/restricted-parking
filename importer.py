#!/usr/bin/env python
# pylint: disable=unused-import,fixme,abstract-class-not-used

from scipy import arange

from importers.yelp import Yelp
from importers.google import Google
from importers.foursquare import Foursquare


class Importer():
  
  # Instance Variables
  search_area = 2 #0.01
  search_areas = {
    "Santa Monica": [
      33.984862, -118.514328,
      34.05056, -118.39777
    ]
#     "United States": [
#       -125.0011, 24.9493, 
#       -66.9326, 49.5904
#     ]
#     "Santa Monica": [
#       34.0170211, -118.49357419999998,
#       34.0170411, -118.49359419999998,
#     ]
  }
  
  importers = [
    Yelp(), Google(), Foursquare()
  ]
  
  # Import Method
  def run(self):
    for name, area in self.search_areas.items():
      lats = sorted([area[0], area[2]])
      lngs = sorted([area[1], area[3]])
     
      for lat in arange(lats[0], lats[1], self.search_area): 
        for lng in arange(lngs[0], lngs[1], self.search_area):
          self.fetch(lat, lng)
      
  
  def fetch(self, lat, lng):    
    for importer in self.importers:
      importer.fetch_data(lat, lng)

      
if __name__ == "__main__":
  Importer().run()