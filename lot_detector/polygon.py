import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial
from queue import Queue
import skimage.io as io
import math
from mercator import GlobalMercator


class PolygonDetector:
  
  zoom = 17
  tile_size = 500
  grayscale_filter = 100
  dot_color = "0x73FF2F"
  dot_color_rgb = [155, 255, 47]
  terrain_base_url = "https://maps.googleapis.com/maps/api/staticmap?style=feature:poi|visibility:simplified&style=feature:administrative|element:all|visibility:off&style=feature:road|element:all|color:0x000000&style=feature:landscape|element:all|color:0xFFFFFF&style=feature:poi|element:all|visibility:off&style=feature:transit|element:labels|visibility:off&style=feature:road|element:labels|visibility:off&key=AIzaSyA4rAT0fdTZLNkJ5o0uaAwZ89vVPQpr_Kc&"
  satellite_base_url = "https://maps.googleapis.com/maps/api/staticmap?maptype=satellite&key=AIzaSyA4rAT0fdTZLNkJ5o0uaAwZ89vVPQpr_Kc&"
  mercator = GlobalMercator(tileSize=tile_size)
  
    
  # Helper Methods    
  def point_to_string(self, point):
    return "%s,%s" % point
    
  
  def bounds_to_string(self, bounds):
    return "|".join([ "%s,%s" % x for x in bounds ])
  
    
  def tile_to_string(self, tile):
    return "%ix%i" % (tile,tile)
    
  
  def fetch_image(self, maptype, params, marker=None):
    url = self.terrain_base_url
    
    if maptype == "satellite":
      url = self.satellite_base_url
    
    if marker:
      params +="&markers=color:%s|size:tiny|%s" % (
        self.dot_color,
        self.point_to_string(marker)
        
      )
    
    print(url + params)
    return io.imread(url + params)
  
  
  def center_image(self, maptype, point, zoom, marker=None):
    params = "center=%s&size=%s&zoom=%i" % (
      self.point_to_string(point),
      self.tile_to_string(self.tile_size),
      zoom
    )
    
    return self.fetch_image(maptype, params, marker=marker)
    
    
  def bounds_image(self, maptype, bounds, zoom, marker=None):
    params = "visible=%s&size=%s&zoom=%i" % (
      self.bounds_to_string(bounds),
      self.tile_to_string(self.tile_size),
      zoom
    )
    
    return self.fetch_image(maptype, params, marker=marker)
  
    
  # Helper Methods
  def grayscale(self, rgb):
    if len(rgb.shape) < 3:
      return rgb
    
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray
    
    
  def neighbors(self, shape, point):
    bounds = [-1, shape[0], shape[1]]
    neighbors = [
      (point[0] + 1, point[1]),
      (point[0] - 1, point[1]),
      (point[0], point[1] + 1),
      (point[0], point[1] - 1)
    ]
    
    def in_shape(test_point):
      return test_point[0] not in bounds and test_point[1] not in bounds
    
    return [ x for x in neighbors if in_shape(x) ]
    
    
  def sort_nearest(self, points, point):
    distances = np.array([ 
      [x, np.linalg.norm(x[1]-point)] for x  in points 
    ])
    
    return [
      x[0] for x in distances[distances[:,1].argsort()]
    ]
    
  
  def mask_image(self, image, polygon):
    temp = image.copy()
    image[:] = 255
    
    for point in polygon:
      image[point] = temp[point]
    
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
    center_image = self.center_image("terrain", point, self.zoom, marker=point)
    (center_polygon, center_bounds) = self.image_search(center_image, point, self.zoom)
    
    self.save_image("centered", center_image)
    self.save_image("test", self.mask_image(center_image, center_polygon))
    
    zoomed_bounds = self.pixel_bounds_to_point_bounds(point, center_bounds, self.zoom)
    zoomed_image = self.bounds_image("terrain", zoomed_bounds, self.zoom + 1, marker=point)
    (zoomed_polygon, zoomed_bounds) = self.image_search(zoomed_image, point, self.zoom + 1)
    
    self.save_image("zoomed", zoomed_image)
    self.save_image("test2", self.mask_image(zoomed_image, zoomed_polygon))
    
  
  def image_find_start(self, image):  
    colors = [
      [x, image[x]] for x in np.ndindex(image.shape[:2]) if len(set(image[x])) > 1
    ]
    sorted_colors = self.sort_nearest(colors, self.dot_color_rgb)     
    return sorted_colors[0][0]
    
    
  def image_find_border(self, image, point):
    array = np.array(np.where(image < self.grayscale_filter)).T
    return tuple(array[spatial.KDTree(array).query(point)[1]])
    
    
  def image_trace_border(self, image, start):
    frontier = Queue()
    frontier.put(start)
    polygon = []
    visited = []
    
    while not frontier.empty():        
      point = frontier.get()
      neighbors = self.neighbors(image.shape, point)
      non_borders = [
        x for x in neighbors if image[x] > self.grayscale_filter
      ]
      
      if len(non_borders) == 0 or len(neighbors) == len(non_borders):
        continue
        
      polygon.append(point)
        
      for neighbor in neighbors:
        if neighbor not in visited:          
          visited.append(neighbor)
          frontier.put(neighbor)
          
    return polygon


  def image_search(self, image, point, zoom):   
    grayscale = self.grayscale(image)
    start = self.image_find_start(image)
    border_point = self.image_find_border(grayscale, start)
    polygon = self.image_trace_border(grayscale, border_point)
    
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
  
