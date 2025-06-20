#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:09:01 2025

@author: ann
"""

import os
import cv2
import numpy as np
from ultralytics import YOLO

# Путь к папке с изображениями
input_image_folder = "/home/ann/Загрузки/License Plates Recognition.v2i.yolov8/train/images"
# Путь к папке для сохранения обработанных изображений
output_image_folder = "/home/ann/Загрузки/License Plates Recognition.v2i.yolov8/train/img1"
# Путь к папке для сохранения разметки
output_label_folder = "/home/ann/Загрузки/License Plates Recognition.v2i.yolov8/train/label1"

# Создаем папки, если они не существуют
os.makedirs(output_image_folder, exist_ok=True)
os.makedirs(output_label_folder, exist_ok=True)

# Загружаем модель YOLOv8
model = YOLO("yolov8n.pt")  # Можно использовать другие версии модели, например, yolov8s.pt, yolov8m.pt и т.д.

# Обрабатываем каждое изображение в папке
for image_name in os.listdir(input_image_folder):
    if not image_name.endswith((".jpg", ".jpeg", ".png")):
        continue

    image_path = os.path.join(input_image_folder, image_name)
    image = cv2.imread(image_path)
    height, width, _ = image.shape

    # Получаем предсказания от модели
    results = model(image)

    # Создаем файл для сохранения разметки
    label_name = os.path.splitext(image_name)[0] + ".txt"
    label_path = os.path.join(output_label_folder, label_name)

    with open(label_path, "w") as label_file:
        for result in results:
            for box in result.boxes:
                # Получаем класс и координаты bounding box
                class_id = int(box.cls)
                if class_id != 2:  # Класс "car" в YOLOv8 имеет индекс 2
                    continue

                # Перезаписываем класс на 0
                class_id = 0

                # Получаем координаты bounding box в формате YOLO (нормализованные)
                x_center = (box.xyxy[0][0] + box.xyxy[0][2]) / 2 / width
                y_center = (box.xyxy[0][1] + box.xyxy[0][3]) / 2 / height
                box_width = (box.xyxy[0][2] - box.xyxy[0][0]) / width
                box_height = (box.xyxy[0][3] - box.xyxy[0][1]) / height

                # Записываем данные в файл
                label_file.write(f"{class_id} {x_center} {y_center} {box_width} {box_height}\n")

    # Сохраняем изображение в выходную папку
    output_image_path = os.path.join(output_image_folder, image_name)
    cv2.imwrite(output_image_path, image)

print("Обработка завершена.")