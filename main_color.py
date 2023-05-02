#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 16:56:41 2023

@author: ann
"""

import cv2
import numpy as np
from scipy.cluster.vq import kmeans,vq
from scipy.cluster.vq import whiten
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

def find_dominant(path):
    image_original = cv2.imread(path)
    #image_original = cv2.cvtColor(image_original, cv2.COLOR_BGR2RGB)
    image_original1 = cv2.cvtColor(image_original, cv2.IMREAD_GRAYSCALE)
    img_blur = cv2.GaussianBlur(image_original1, (3,3), 0)
    
    edge = cv2.Canny(img_blur, 20, 30)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(9,9))
    dilated = cv2.dilate(edge, kernel)
    contours, hierarchy = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours) != 0:
        c = max(contours, key = cv2.contourArea)
        x,y,w,h = cv2.boundingRect(c)
        
    
    cropped_image = image_original[y:y+h, x:x+w]
    cv2.imwrite("crop.png", cropped_image)
    
    
    pixels = cropped_image.reshape((-1, 3))
    r,g,b=[],[],[]
    k_means= KMeans(n_clusters=5)
    k_means.fit(pixels)
    colors = np.asarray(k_means.cluster_centers_, dtype='uint8')
    pixels_colourwise = np.unique(k_means.labels_, return_counts=True)[1]
    percentage_max = max(pixels_colourwise/pixels.shape[0])
    #print(percentage_max)
    percentage = pixels_colourwise/pixels.shape[0]
    #print( percentage )
    #print( len( percentage ) )
    percentage_max_index = percentage.tolist().index(percentage_max)
    #print(percentage_max_index)
    #print(colors[percentage_max_index])    
    RGB = colors[percentage_max_index]
    
    create_label(RGB)
    
    return RGB

def create_label(RGB):
    image = np.zeros((200, 200, 3), np.uint8)
    image[:] = (RGB)
    
    return cv2.imshow("label", image)

if __name__ == "__main__":
    path = "/home/ann/DOMINATION_COLOR/apple-fruit.jpg"
    print(find_dominant(path))
    
    
    cv2.waitKey(0)    
    # Closes all the frames
    cv2.destroyAllWindows()
    
    