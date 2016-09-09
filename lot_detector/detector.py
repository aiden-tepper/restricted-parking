import numpy as np
from scipy import spatial
from queue import Queue
import math
import skimage.filters as filters
import matplotlib.pyplot as plt
from matplotlib.path import Path

from utils import PolygonUtils
from regions import PolygonRegions
from profiler import PolygonProfiler, PolygonProfile


class PolygonDetector:
  
  # Instance variables 
  zoom = 20
  debug = True
  utils = PolygonUtils()
  regions = PolygonRegions()
  profiler = PolygonProfiler()


  # Instance Methods
  def search(self, point):
    terrain_polygon = self.search_terrain(point)
    lot_paths = self.search_satellite(point, terrain_polygon)
    
    for path in lot_paths:
      polygon = path.to_polygons()[0]
      bounds = [
        (np.amin(polygon[0]), np.amax(polygon[1])),
        (np.amax(polygon[0]), np.amin(polygon[1]))
      ]
      
      # TODO: lat/lng generated are shifted/off
      print(self.utils.pixel_bounds_to_point_bounds(point, bounds, self.zoom))
    
    
  def search_terrain(self, point):  
    image = self.utils.center_image("terrain", point, self.zoom, marker=point)
    (polygon, bounds) = self.image_border_search(image, point, self.zoom)
    return polygon
    
    
  def search_satellite(self, point, polygon):    
    polygon_path = Path(polygon, closed=True)
    image = self.utils.center_image("satellite", point, self.zoom)
    masked_image = self.utils.mask_image(image, polygon)
    grayscale_image = self.utils.grayscale(masked_image)
    lot_paths = []
    
    edge_image = filters.prewitt(grayscale_image)
    edge_regions = self.regions.search(edge_image)
    
    for region in edge_regions:
      region_image = masked_image[region[0][0]:region[1][0], region[0][1]:region[1][1], :]
      profile = self.profiler.profile(region_image)
      
      if profile == PolygonProfile.LOT:
        bbox = self.utils.region_to_bbox(region)
        lot_paths.append(polygon_path.clip_to_bbox(bbox, inside=True))
    
    if self.debug and len(lot_paths) > 0:
      self.utils.draw_path_on_image(image, lot_paths)
    
    return lot_paths
    
  
  def image_find_start(self, image):  
    colors = [
      [x, image[x]] for x in np.ndindex(image.shape[:2]) if len(set(image[x])) > 1
    ]
    sorted_colors = self.utils.sort_nearest(colors, self.utils.dot_color_rgb)     
    return sorted_colors[0][0]
    
    
  def image_find_border(self, image, point):
    array = np.array(np.where(image < self.utils.grayscale_filter)).T
    return tuple(array[spatial.KDTree(array).query(point)[1]])
    
    
  def image_trace_border(self, image, start):
    frontier = Queue()
    frontier.put(start)
    polygon = []
    visited = []
    bounds = [0, self.utils.tile_size-1]
    
    while not frontier.empty():        
      point = frontier.get()
      neighbors = self.utils.neighbors(image.shape, point)
      non_borders = [
        x for x in neighbors if image[x] > self.utils.grayscale_filter
      ]
      
      if len(non_borders) == 0 or (len(neighbors) == len(non_borders) and self.utils.in_shape(bounds, point)):      
        continue
      
      polygon.append(point)
        
      for neighbor in neighbors:
        if neighbor not in visited:          
          visited.append(neighbor)
          frontier.put(neighbor)
          
    return polygon


  def image_border_search(self, image, point, zoom):   
    grayscale = self.utils.grayscale(image)
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
  points = [
    (34.0039417, -118.4858517),
#     (34.0027721, -118.4846514),
#     (34.0009191, -118.4842381),
#     (34.0003494, -118.4861325),
#     (34.0014563, -118.483333),
#     (34.0022385, -118.4883279),
#     (34.0036698, -118.4847942),
#     (33.9993226, -118.4811244),
  ]
  
  for point in points:  
    detector = PolygonDetector()
    detector.search(point)
  
