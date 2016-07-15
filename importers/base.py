from builtins import object
import googlemaps as gmaps

class Base(object):
  """Override this in your derived class."""
  
  debug = False
  gmaps = gmaps.Client(key='AIzaSyCQdXjYOfGZq37rCE0pD55Mmi0I-m7q0Ss')
  
  
  def fetch_data(self, lat, lng):
    raise NotImplementedError('Must override this method in your derived Class')
  
  

class Venue(object):
  
  name = None
  address = None
  lat = None
  lng = None
  source = None
  city = None
  phone = None
  yelp_id = None
  
  
  def __init__(self, **kwargs):
    for key, value in list(kwargs.items()):
      setattr(self, key, value)

  
  def __setattr__(self, key, value):
    """
    We want to prevent importers from adding invalid attributes (PWS-317)
    For example, accidentally calling "avail" "available"
    Rather fail hard in these cases.
    """
    if not hasattr(self, key):
      raise TypeError("Cannot create attribute %s, Data is a frozen class" % key)
    
    object.__setattr__(self, key, value)