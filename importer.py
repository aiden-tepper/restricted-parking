#!/usr/bin/env python
# pylint: disable=unused-import,fixme,abstract-class-not-used

from scipy import arange
import math, sys

from importers.yelp import Yelp
from importers.google import Google
from importers.foursquare import Foursquare


class Importer():

  # Instance Variables
  search_offset = 5000
  search_boxes = {
    "Santa Monica": [
      [33.984862, -118.514328],
      [34.05056, -118.39777]
    ]
  }

  venues = []
  importers = [
    Yelp(), Google(), Foursquare()
  ]

  # Import Method
  def run(self):
    # Fetch venues for point
    for name, box in self.search_boxes.items():
      for location in self.locations(box): # for each grid dot
        self.fetch(location[0], location[1])


  def fetch(self, lat, lng):
    for importer in self.importers:
      importer.fetch(lat, lng)
      importer.upload(lat, lng)


  def locations(self, box):
    locations = []
    R = 6378137 # earth's radius

    lats = sorted([box[0][0], box[1][0]]) # sorts x corners (latitude)
    lngs = sorted([box[0][1], box[1][1]]) # sorts y corners (longitude)
    lat = lats[0]
    latIncr = 0

    while lat < lats[1]:
      latOffset = self.search_offset * latIncr
      lat = lat + latOffset/R * 180/math.pi
      latIncr += 1

      lng = lngs[0]
      lngIncr = 0

      while lng < lngs[1]:
        lngOffset = self.search_offset * lngIncr
        lng = lng + lngOffset/(R * math.cos(math.pi  * lat/180)) * 180/math.pi
        lngIncr += 1
        locations.append([lat, lng])
        """
        ---->
        ---->^
        """

    return locations # returns grid of coordinate points between corners


if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print("Please provide a ParkMe API! Ex: http://api.parkme.com")
    sys.exit(1)

  importer = Importer()
  importer.run()
