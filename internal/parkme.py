import requests, sys

class ParkMe:
  
  base_url = sys.argv[1]
  lot_url = base_url + "/lot"
  destination_url = base_url + "/destination"
  user = '7e7e5a90-5534-11e2-82e7-22000af90521' # jenkins user
  
  def add_lot(self, venue): 
    response = requests.post(self.lot_url, data={
      "lat": venue.lat,
      "lng": venue.lng,
      "address": venue.address,
      "user": self.user,
      "destination": self.get_destination(venue),
      "restrictive": True
    })
    
    if "Created" in response.text:
      print("PARKME UPLOAD:", venue.name, "---", venue.address)
    
    
  def get_destination(self, venue):
    if venue.lat is None or venue.lng is None:
      return None
        
    response = requests.get(self.destination_url, params={
      "pt": "%f|%f|%i" % (venue.lng, venue.lat, 50),
      "name": venue.name,
      "user": self.user,
      "pub_id": "1",
      
    })
    
    destinations = response.json()["Destinations"]
    
    if len(destinations) > 0 and destinations[0]["distance"] < 50:
      return destinations[0]["slug"]
    
    return None