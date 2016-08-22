import numpy as np
import matplotlib.patches as mpatches

from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label
from skimage.morphology import closing, square, skeletonize
from skimage.measure import regionprops
from skimage.color import label2rgb
from utils import PolygonUtils


class PolygonRegions():
  
  # Instance variables 
  utils = PolygonUtils()

  
  # Instance methods
  def search(self, image):
    image = self.utils.grayscale(image)
    cleared_image = self.threshold_image(image)
    return self.image_regions(cleared_image)
    
    
  def threshold_image(self, image):
    thresh = threshold_otsu(image)
    bw = closing(image > thresh, square(11))
    cleared = bw.copy()
    clear_border(cleared)
    return ~cleared
    
  
  def image_regions(self, image):
    total_area = image.shape[0] * image.shape[1]
    label_image = label(image)
    image_label_overlay = label2rgb(label_image, image=image)
    regions = []
    
    for region in regionprops(label_image):
      minr, minc, maxr, maxc = region.bbox
      area = (maxc - minc) * (maxr - minr)
    
      # skip small or super large regions
      if area < (total_area * 0.02) or area > (total_area * 0.7):
          continue 
          
      regions.append((minr, minc, maxr, maxc))
    
    return regions