from importers.base import Base, Venue
import requests
from bs4 import BeautifulSoup

class Yelp(Base):

  base_url = "https://www.yelp.com/search?"
  debug = False
  
  def request(self, parameters):
    if self.debug:
      f = open('samples/yelp.html', 'r')
      return BeautifulSoup(f.read(), 'html.parser')

    r = requests.get(self.base_url, params=parameters)
    return BeautifulSoup(r.text, 'html.parser')

  
  def extract_venues(self, soup, venues):
    for result in soup.find_all("li", class_ = "regular-search-result"):
      a_node = result.find("a", class_ = "biz-name")
      address_node = result.find("address")
      city_node = result.find("span", class_ = "neighborhood-str-list")
      phone_node = result.find("span", class_ = "biz-phone")
      address = None
      city = None
      phone = None
      locations = []
      
      if address_node is not None:
        address = address_node.getText("").strip()
        locations = self.gmaps.geocode(address)
      
      if city_node is not None:
        city = city_node.getText().strip()
      
      if phone_node is not None:
        phone = phone_node.getText().strip()
      
      venue = Venue(
        source = "yelp",
        name = a_node.getText(),
        yelp_id = a_node["href"].replace("/biz/", ""),
        address = address,
        city = city,
        phone = phone
      )
      
      if len(locations) > 0:      
        venue.lat = locations[0]["geometry"]["location"]["lat"]
        venue.lng = locations[0]["geometry"]["location"]["lng"]
      
      print("YELP: " + venue.name)
      venues.append(venue)
      
      
  def next_page(self, soup):
    current = soup.find("div", {
      "class": [
        "page-option", "current"
      ]
    })
    
    if current is None
      return None
    
    return current.findNext('div', class_ = "page-option") 
      
        
  def fetch_data(self, lat, lng, venues = []):  
    addresses = self.gmaps.reverse_geocode((lat, lng))
    
    if len(addresses) == 0:
      return []
    
    soup = self.request({
      "find_loc": addresses[0]["formatted_address"],
      "start": len(venues),
      "attrs": "BusinessParking.lot"
    })
    
    self.extract_venues(soup, venues)
    
    if self.next_page(soup) is not None:
      return self.fetch_data(lat, lng, venues)
    
    return venues
      