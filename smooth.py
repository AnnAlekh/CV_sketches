#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 15 11:02:24 2024

@author: ann
"""

import os
import shutil

import cv2

def is_blurry(image_path, threshold=50):
    # Загружаем изображение
    image = cv2.imread(image_path)
    
    # Преобразуем изображение в оттенки серого
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Вычисляем градиенты изображения
    gradient = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Если градиенты ниже порога, считаем изображение смазанным
    return gradient < threshold

# Путь к изображению, которое нужно проверить на смазанность

# Пороговое значение для определения смазанности изображения
threshold = 50


source_folder = '/home/ann/Downloads/cedar_15.05.2024'
destination_folder = '/home/ann/Downloads/cedar_smooth'

# Проверяем, существует ли целевая папка, и создаем ее, если она отсутствует
if not os.path.exists(destination_folder):
    os.makedirs(destination_folder)

# Получаем список файлов из исходной папки
files = os.listdir(source_folder)

for file in files:
    if file.endswith('.jpg') or file.endswith('.jpeg') or file.endswith('.png'):
        
        if is_blurry(os.path.join(source_folder, file)):
        # Проверяем, является ли изображение смазанным (здесь можно добавить свою логику для определения смазанных изображений)
        # Например, можно использовать библиотеку OpenCV для анализа качества изображения

        # Перемещаем смазанные изображения в целевую папку
            shutil.move(os.path.join(source_folder, file), os.path.join(destination_folder, file))

print("Смазанные изображения были перемещены в целевую папку.")