import numpy as np
from enum import Enum
import matplotlib.pyplot as plt


class PolygonProfile(Enum):
  
  LOT, UNKNOWN = range(2)


class PolygonProfiler:
  
  # Instnce methods
  def profile(self, image):
    flattened_image = image.reshape(-1, 3)
    masked_image = np.array([color for color in flattened_image if np.any(color != 255)])
    
    red = masked_image[:,0].flatten()
    green = masked_image[:,1].flatten()
    blue = masked_image[:,2].flatten()
    
    profile = self.classify({
      "red": np.histogram(red, 25, range=(0,255))[0],
      "green": np.histogram(green, 25, range=(0,255))[0],
      "blue": np.histogram(blue, 25, range=(0,255))[0]
    })
    
    if True or profile == PolygonProfile.LOT:
      self.plot_debug(image, [
        [red, "red"],
        [green, "green"],
        [blue, "blue"]
      ])
       
    return profile
    
    
  
  def classify(self, histograms):
    if self.is_lot(histograms):
      return PolygonProfile.LOT
    
    return PolygonProfile.UNKNOWN
    
    
  def is_lot(self, histograms):
    mostly_gray = []
    
    for color, histogram in histograms.items():
      gray_sum = histogram[1:8].sum()
      total_sum = histogram.sum()
      mostly_gray.append(gray_sum/total_sum > 0.75)
      #print(color, gray_sum/total_sum)
     
    return np.array(mostly_gray).all()
    
    
  def plot_debug(self, image, graphs):
    fig, axes = plt.subplots(nrows=2, ncols=2, sharex=False, sharey=False)
    axes = axes.flatten()
    axes[0].imshow(image)
    
    for i, axe in enumerate(axes[1:]):
      graph = graphs[i]
      axe.hist(graph[0], 25, normed=False, range=(0,255), color=graph[1])
   
    plt.show()