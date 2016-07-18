import requests

class ParkMe:
  
  base_url = "http://api.dev01.parkme.com"
  lot_url = base_url + "/lot"
  destination_url = base_url + "/destination"
  user = '7e7e5a90-5534-11e2-82e7-22000af90521' # jenkins user
  
  def add_lot(self, venue, destination=None):    
    response = requests.post(self.lot_url, data={
      "lat": venue.lat,
      "lng": venue.lng,
      "address": venue.address,
      "user": self.user
    })
    
    if "Created" in response.text:
      print("PARKME UPLOAD:", venue.name, "---", venue.address)
    
    
  def destinations(self, lat, lng):
    response = requests.get(self.destination_url, params={
      "pt": "%f|%f|%i" % (lat, lng, 5000),
      "user": self.user,
      "pub_id": ""
    })
    
    print(response.text)