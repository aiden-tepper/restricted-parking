import numpy as np
import matplotlib.pyplot as plt
from scipy import spatial
from queue import Queue
import skimage.io as io
import math
from mercator import GlobalMercator
from PIL import Image, ImageDraw
from skimage import feature
import skimage.filters as filters



class PolygonDetector:
  
  zoom = 20
  tile_size = 500
  grayscale_filter = 100
  dot_color = "0x73FF2F"
  dot_color_rgb = [155, 255, 47]
  base_url = "https://maps.googleapis.com/maps/api/staticmap?style=feature:poi|visibility:simplified&style=feature:administrative|element:all|visibility:off&style=feature:road|element:all|color:0x000000&style=feature:landscape|element:all|color:0xFFFFFF&style=feature:poi|element:all|visibility:off&style=feature:transit|element:labels|visibility:off&style=feature:road|element:labels|visibility:off&key=AIzaSyA4rAT0fdTZLNkJ5o0uaAwZ89vVPQpr_Kc&"
  mercator = GlobalMercator(tileSize=tile_size)
  
    
  # Helper Methods    
  def point_to_string(self, point):
    return "%s,%s" % point
    
  
  def bounds_to_string(self, bounds):
    return "|".join([ "%s,%s" % x for x in bounds ])
  
    
  def tile_to_string(self, tile):
    return "%ix%i" % (tile,tile)
    
  
  def fetch_image(self, maptype, params, marker=None):    
    if maptype == "satellite":
      params += "&maptype=satellite"
    
    if marker:
      params += "&markers=color:%s|size:tiny|%s" % (
        self.dot_color,
        self.point_to_string(marker)
        
      )
    
    print(self.base_url + params)
    return io.imread(self.base_url + params)
  
  
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
    
  
  def in_shape(self, bounds, point):
    return point[0] not in bounds and point[1] not in bounds
    
    
  def neighbors(self, shape, point):
    bounds = [-1, shape[0], shape[1]]
    neighbors = [
      (point[0] + 1, point[1]),
      (point[0] - 1, point[1]),
      (point[0], point[1] + 1),
      (point[0], point[1] - 1)
    ]
    
    return [ x for x in neighbors if self.in_shape(bounds, x) ]
    
    
  def sort_nearest(self, points, point):
    distances = np.array([ 
      [x, np.linalg.norm(x[1]-point)] for x  in points 
    ])
    
    return [
      x[0] for x in distances[distances[:,1].argsort()]
    ]
    
  
  def mask_image(self, image, polygon):  
    # Flip coordinates for the mask
    for i, point in enumerate(polygon):
      polygon[i] = (point[1], point[0])
    
    img = Image.new('L', image.shape[:2], 0)
    ImageDraw.Draw(img).polygon(polygon, outline=1, fill=1)
    mask = np.logical_not(np.array(img, dtype=bool))

    temp = image.copy()
    temp[mask] = 255   
    
    return temp
    
  
  def save_image(self, name, image):
    plt.imsave("samples/%s.png" % name, image, cmap=plt.cm.gray)

  
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
    polygon = self.search_terrain(point)
    self.search_satellite(point, polygon)
    
    
  def search_terrain(self, point):  
    image = self.center_image("terrain", point, self.zoom, marker=point)
    (polygon, bounds) = self.image_border_search(image, point, self.zoom)
    return polygon
    
    
  def search_satellite(self, point, polygon):
    image = self.center_image("satellite", point, self.zoom)
    masked_image = self.mask_image(image, polygon)
    grayscale_image = self.grayscale(masked_image)
    
    edge_image = filters.prewitt(grayscale_image)
    
    self.save_image("edge", edge_image)
    
    
  
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
    bounds = [0, self.tile_size-1]
    
    while not frontier.empty():        
      point = frontier.get()
      neighbors = self.neighbors(image.shape, point)
      non_borders = [
        x for x in neighbors if image[x] > self.grayscale_filter
      ]
      
      if len(non_borders) == 0 or (len(neighbors) == len(non_borders) and self.in_shape(bounds, point)):      
        continue
      
      polygon.append(point)
        
      for neighbor in neighbors:
        if neighbor not in visited:          
          visited.append(neighbor)
          frontier.put(neighbor)
          
    return polygon


  def image_border_search(self, image, point, zoom):   
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
  
