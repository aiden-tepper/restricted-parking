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
      data_file = open('samples/foursquare.json')  
      return json.load(data_file)
    
    return self.client.venues.explore(params=params)

    
  def fetch_data(self, lat, lng, venues = []):     
    results = self.request({
      "ll": "%.8f,%.8f" % (lat, lng),
      "radius": 5000,
      "limit": 50,
      "offset": len(venues),
      "query": "free parking"
    })
    
    if not results["groups"][0]["items"]:
      return venues
    
    for group in results["groups"]:
      for item in group["items"]:
        place = item["venue"]
        
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
        
        print("FOURSQUARE: " + venue.name)
        venues.append(venue)
      
    return self.fetch_data(lat, lng, venues)