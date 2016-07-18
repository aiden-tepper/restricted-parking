import googlemaps as gmaps
from builtins import object
from internal.parkme import ParkMe

class Base:
  """Override this in your derived class."""
  
  debug = False
  venues = {}
  to_save = []
  parkme = ParkMe()
  gmaps = gmaps.Client(key='AIzaSyCQdXjYOfGZq37rCE0pD55Mmi0I-m7q0Ss')
  
  
  def fetch(self, lat, lng):
    raise NotImplementedError('Must override this method in your derived Class')
    
    
  def upload(self, lat, lng):
    destinations = self.parkme.destinations(lat, lng)
    
    for venue in self.to_save:
      self.parkme.add_lot(venue)
    
    self.to_save = []
  

class Venue(object):
  
  name = None
  address = None
  lat = None
  lng = None
  source = None
  city = None
  phone = None
  yelp_id = None
  google_id = None
  foursquare_id = None
  
  
  def __init__(self, **kwargs):
    for key, value in list(kwargs.items()):
      setattr(self, key, value)

  
  def __setattr__(self, key, value):
    """
    We want to prevent importers from adding invalid attributes (PWS-317)
    Rather fail hard in these cases.
    """
    if not hasattr(self, key):
      raise TypeError("Cannot create attribute %s, Data is a frozen class" % key)
    
    object.__setattr__(self, key, value)