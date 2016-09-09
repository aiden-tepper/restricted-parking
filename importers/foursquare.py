from importers.base import Base, Venue
import foursquare, json

class Foursquare(Base):
  
  debug = False
  client = foursquare.Foursquare(
    client_id='AQRHOGWFS02HFHSCW5ODX0F523AO5XKTONJW0KSL3HXBS15J', 
    client_secret='UFKEOI5TB5Y5QRCHWCHEKHC3S22FJR3WKNUWLSMWPHHKZNXW'
  )
  
  
  def request(self, params):
    if self.debug:
      data_file = open('importers/samples/foursquare.json')  
      return json.load(data_file)
    
    return self.client.venues.explore(params=params)

    
  def fetch(self, lat, lng, offset = 0):     
    results = self.request({
      "ll": "%.8f,%.8f" % (lat, lng),
      "radius": 5000,
      "limit": 50,
      "offset": offset,
      "query": "free parking"
    })
    
    for group in results["groups"]:
      for item in group["items"]:
        place = item["venue"]
        offset += 1
        
        venue = Venue(
          source = "foursquare",
          name = place["name"],
          foursquare_id = place["id"],
          address = " ".join(place["location"]["formattedAddress"]),
          lat = place["location"]["lat"],
          lng = place["location"]["lng"],
          city = place["location"].get("city"),
          phone = place["contact"].get("formattedPhone")
        )
        
        if venue.foursquare_id not in self.venues:
          print("FOURSQUARE: " + venue.name)
          self.to_save.append(venue)
          self.venues[venue.foursquare_id] = venue
     
    if results["groups"][0]["items"]: 
      self.upload(lat, lng)
      return self.fetch(lat, lng, offset)
