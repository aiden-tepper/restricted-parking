import requests

class ParkMe:
  
  base_url = "http://api.dev01.parkme.com"
  lot_url = base_url + "/lot"
  destination_url = base_url + "/destination"
  user = '7e7e5a90-5534-11e2-82e7-22000af90521' # jenkins user
  
  def add_lot(self, venue): 
    response = requests.post(self.lot_url, data={
      "lat": venue.lat,
      "lng": venue.lng,
      "address": venue.address,
      "user": self.user,
      "destination": self.destination(venue),
      "is_destination": True
    })
    
    if "Created" in response.text:
      print("PARKME UPLOAD:", venue.name, "---", venue.address)
    
    
  def destination(self, venue):
    response = requests.get(self.destination_url, params={
      "pt": "%f|%f|%i" % (venue.lng, venue.lat, 500),
      "name": venue.name,
      "user": self.user,
      "pub_id": "1",
      
    })
    
    destinations = response.json()["Destinations"]
    
    if len(destinations) > 0:
      return destinations[0]["slug"]
    
    return None