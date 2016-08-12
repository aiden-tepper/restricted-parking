import numpy as np
import matplotlib.pyplot as plt
from queue import Queue
import skimage.io as io
import math
from mercator import GlobalMercator


class PolygonDetector:
  
  zoom = 17
  tile_size = 500
  terrain_base_url = "https://maps.googleapis.com/maps/api/staticmap?maptype=terrain&style=feature:administrative|element:all|visibility:off&style=feature:road|element:all|color:0x000000&style=feature:landscape|element:all|color:0xFFFFFF&style=feature:poi|element:all|visibility:off&style=feature:transit|element:labels|visibility:off&style=feature:road|element:labels|visibility:off&key=AIzaSyA4rAT0fdTZLNkJ5o0uaAwZ89vVPQpr_Kc&"
  satellite_base_url = "https://maps.googleapis.com/maps/api/staticmap?maptype=satellite&key=AIzaSyA4rAT0fdTZLNkJ5o0uaAwZ89vVPQpr_Kc&"
  mercator = GlobalMercator(tileSize=tile_size)
  
    
  # Helper Methods    
  def point_to_string(self, point):
    return "%s,%s" % point
    
  
  def bounds_to_string(self, bounds):
    return "|".join([ "%s,%s" % x for x in bounds ])
  
    
  def tile_to_string(self, tile):
    return "%ix%i" % (tile,tile)
    
  
  def fetch_image(self, maptype, params):
    url = self.terrain_base_url
    
    if maptype == "satellite":
      url = self.satellite_base_url
    
    print(url + params)
    return io.imread(url + params)
  
  
  def center_image(self, maptype, point, zoom):
    params = "center=%s&size=%s&zoom=%i" % (
      self.point_to_string(point),
      self.tile_to_string(self.tile_size),
      zoom
    )
    
    return self.fetch_image(maptype, params)
    
    
  def bounds_image(self, maptype, bounds, zoom):
    params = "visible=%s&size=%s&zoom=%i" % (
      self.bounds_to_string(bounds),
      self.tile_to_string(self.tile_size),
      zoom
    )
    
    return self.fetch_image(maptype, params)
  
    
  # Help Methods
  def grayscale(self, rgb):
    if len(rgb.shape) < 3:
      return rgb
    
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray
    
  
  def in_shape(self, shape, point):
    bounds = [-1, shape[0], shape[1]]
    return point[0] not in bounds and point[1] not in bounds
    
    
  def neighbors(self, point):
    return [
      (point[0] + 1, point[1]),
      (point[0], point[1] + 1),
      (point[0] - 1, point[0]),
      (point[0], point[1] - 1)
    ]
    
  
  def mask_image(self, image, polygon):
    temp = image.copy()
    image[:] = 0
    
    for cords in polygon:
      image[cords] = temp[cords]
    
    return image
    
  
  def save_image(self, name, image):
    plt.imsave("samples/%s.png" % name, image)

  
  # Mercator Helper Methods
  def point_to_pixels(self, point, zoom):
    meters = self.mercator.LatLonToMeters(point[0], point[1])
    return self.mercator.MetersToPixels(meters[0], meters[1], zoom)
  
  
  def pixels_to_point(self, pixels, zoom):
    meters = self.mercator.PixelsToMeters(pixels[0], pixels[1], zoom)
    return self.mercator.MetersToLatLon(meters[0], meters[1])
  
  
  def pixels_to_bounds(self, pixels, zoom):
    tile = self.mercator.PixelsToTile(pixels[0], pixels[1])
    bounds = self.mercator.TileLatLonBounds(tile[0], tile[1], zoom)
    return [
      self.point_to_pixels((bounds[0], bounds[1]), zoom),
      self.point_to_pixels((bounds[2], bounds[3]), zoom)
    ]
    
  
  def pixel_bounds_to_point_bounds(self, center, bounds, zoom):
    pixels = self.point_to_pixels(center, zoom)
    pixel_bounds = self.pixels_to_bounds(pixels, zoom)
    pixels_corner = (pixel_bounds[0][0], pixel_bounds[1][1])
    return [
      self.pixels_to_point((pixels_corner[0] + bounds[0][0], pixels_corner[1] - bounds[0][1]), zoom),
      self.pixels_to_point((pixels_corner[0] + bounds[1][0], pixels_corner[1] - bounds[1][1]), zoom)
    ]
  
  
  # Image Search Methods
  def search(self, point):
    self.search_terrain(point)
    
    
  def search_terrain(self, point):
    center_image = self.center_image("terrain", point, self.zoom)
    (center_polygon, center_bounds) = self.image_search(center_image)
    
    self.save_image("test", self.mask_image(center_image, center_polygon))
    
    zoomed_bounds = self.pixel_bounds_to_point_bounds(point, center_bounds, self.zoom)
    zoomed_image = self.bounds_image("terrain", zoomed_bounds, self.zoom + 1)
    #(zoomed_polygon, zoomed_bounds) = self.image_search(zoomed_image)
    
    print(zoomed_image.shape)
    self.save_image("zoomed", zoomed_image)
    #self.save_image("zoomed", self.mask_image(zoomed_image, zoomed_polygon))
  
  
  def image_search(self, image):
    grayscale = self.grayscale(image)
    start = tuple(int(x/2) for x in grayscale.shape)
    frontier = Queue()
    frontier.put(start)
    mask = np.where(grayscale > 30)
    potentials = { tuple(x): True for x in np.array(mask).T }
    polygon = []
    visited = []
        
    while not frontier.empty():        
      current = frontier.get()
      
      for point in self.neighbors(current):
        if point in visited or not self.in_shape(grayscale.shape, point):
          continue
      
        visited.append(point)
      
        if point in potentials:
          frontier.put(point)
          polygon.append(point)
    
    xs = [int(i[0]) for i in polygon]
    ys = [int(i[1]) for i in polygon]
    bounding_box = [
      [min(xs), min(ys)],
      [(max(xs)+1), (max(ys)+1)]
    ]
    
    return (polygon, bounding_box)
    
    
if __name__ == "__main__":
  starter_point = (34.0039417,-118.4858517)
  
  detector = PolygonDetector()
  detector.search(starter_point)
  
