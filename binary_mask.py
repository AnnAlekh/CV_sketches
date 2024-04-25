#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 17:24:45 2024

@author: ann
"""

import cv2

# Загрузка изображения керна дерева
image = cv2.imread('/home/ann/KERN/ishodn.tif', cv2.IMREAD_GRAYSCALE)
kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
clear_im=cv2.dilate(image, kernel)
clear_im=cv2.erode(clear_im, kernel)
bg=cv2.GaussianBlur(clear_im,(371,371), 0)
result_im=cv2.subtract(~clear_im, ~bg)
result_im=cv2.multiply(result_im, 3.4)
resized_mask1 = cv2.resize(result_im, (1280, 720))
cv2.imshow('clear.png', resized_mask1)
# Применение пороговой обработки для создания бинарной маски
_, binary_mask = cv2.threshold(result_im, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

# Применение пороговой обработки для удаления ярких пикселей
_, thresholded_image = cv2.threshold(result_im, 200, 255, cv2.THRESH_BINARY_INV)

# Объединение порогованного изображения с исходным изображением
processed_image = cv2.bitwise_and(result_im, result_im, mask=thresholded_image)

processed_image = cv2.multiply(processed_image, 5.0)  # Умножение на коэффициент 5.0 для усиления значений пикселей

# Отображение обработанного изображения
resized_processed_image = cv2.resize(processed_image, (1280, 720))
cv2.imshow('processed_image.png', resized_processed_image)






cv2.waitKey(0)
cv2.destroyAllWindows()