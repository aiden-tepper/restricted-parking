from importers.base import Base, Venue
import json,time

class Google(Base):
  
  debug = False
  
  def request(self, params):
    if self.debug:
      data_file = open('samples/google.json')  
      return json.load(data_file)
    
    return self.gmaps.places(
      params["keyword"],
      location = params["location"], 
      radius = params["radius"],
      page_token = params["next"]
    )
    
    
  def filter(self, places):
    places["results"] = [
      x for x in places["results"] if "parking" not in x["types"]
    ]
    
    return places
  
  
  def fetch_data(self, lat, lng, next = None, venues = []): 
    results = self.filter(self.request({
      "location": [lat, lng],
      "radius": 5000,
      "keyword": "free parking",
      "next": next
    }))
    
    for place in results["results"]:
      venue = Venue(
        source = "google",
        name = place["name"],
        google_id = place["place_id"],
        address = place["formatted_address"],
        lat = place["geometry"]["location"]["lat"],
        lng = place["geometry"]["location"]["lng"]
      )
      
      print("GOOGLE: " + venue.name)
      venues.append(venue)
    
    if "next_page_token" in results:	
      time.sleep(2)
      self.fetch_data(lat, lng, results["next_page_token"], venues)
      
    return venues