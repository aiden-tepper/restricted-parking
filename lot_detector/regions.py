import numpy as np
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
    image = self.utils.grayscale(image) # grayscaled masked edged satellite photo
    cleared_image = self.threshold_image(image) # thresholded image?
    return self.image_regions(cleared_image)


  def threshold_image(self, image):
    thresh = threshold_otsu(image)
    bw = closing(image > thresh, square(11))
    cleared = bw.copy()
    clear_border(cleared)
    return ~cleared


  def image_regions(self, image):
    total_area = image.shape[0] * image.shape[1] # 250,000
    label_image = label(image) # ??
    image_label_overlay = label2rgb(label_image, image=image) # ??
    regions = []

    for region in regionprops(label_image):
      minr, minc, maxr, maxc = region.bbox # (0,0,42,48) changes
      area = (maxc - minc) * (maxr - minr) # 2016 changes

      # skip small or super large regions
      if area < (total_area * 0.02) or area > (total_area * 0.7): # 5,000.0<area<175,000
          continue

      regions.append([(minr, minc), (maxr, maxc)]) # maxr = 42, maxc = 48, min = 0

    return regions
