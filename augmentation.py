#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 13:42:27 2024

@author: ann
"""

import os
import cv2
import numpy as np
import albumentations as A
from tqdm import tqdm  # Импортируем tqdm

# Параметры
images_dir = '/home/ann/Downloads/dataset/train/images'  # Путь к директории с изображениями
labels_dir = '/home/ann/Downloads/dataset/train/labels'  # Путь к директории с аннотациями
output_images_dir = '/home/ann/Downloads/dataset/output/images'  # Путь для сохранения аугментированных изображений
output_labels_dir = '/home/ann/Downloads/dataset/output/labels'  # Путь для сохранения аугментированных аннотаций
augmentation_factor = 10  # Количество новых образцов для создания
target_class_id = 3  # Идентификатор класса Bcoagulans

# Функция для чтения аннотаций в формате YOLO
def read_yolo_annotations(label_file):
    with open(label_file, 'r') as f:
        annotations = []
        for line in f.readlines():
            parts = line.strip().split()
            class_id = int(parts[0])
            bbox = list(map(float, parts[1:]))
            annotations.append((class_id, bbox))
    return annotations

# Функция для записи аннотаций в формате YOLO
def write_yolo_annotations(label_file, annotations):
    with open(label_file, 'w') as f:
        for class_id, bbox in annotations:
            f.write(f"{class_id} {' '.join(map(str, bbox))}\n")

# Аугментация изображений и аннотаций
def augment_image_and_annotations(image_path, annotations):
    image = cv2.imread(image_path)
    
    # Создание аугментации
    transform = A.Compose([
        A.HorizontalFlip(p=0.5),
        A.RandomBrightnessContrast(p=0.5),
        A.Rotate(limit=30, p=0.5),
        A.GaussianBlur(blur_limit=(3, 7), p=0.5),
        A.Resize(height=image.shape[0], width=image.shape[1])  # Сохраняем размер изображения
    ])

    augmented_data = transform(image=image)
    augmented_image = augmented_data['image']

    # Преобразование аннотаций
    height, width, _ = image.shape
    new_annotations = []
    
    for class_id, bbox in annotations:
        if class_id == target_class_id:  # Проверка на целевой класс
            x_center, y_center, w, h = bbox
            
            # Преобразуем координаты из нормализованного формата в пиксели
            x_center_pixel = int(x_center * width)
            y_center_pixel = int(y_center * height)
            w_pixel = int(w * width)
            h_pixel = int(h * height)

            # Применяем аугментацию к координатам (например, поворот)
            # Здесь можно добавить дополнительные преобразования для bbox

            # Нормализуем обратно
            new_x_center = x_center_pixel / width
            new_y_center = y_center_pixel / height
            new_w = w_pixel / width
            new_h = h_pixel / height

            new_annotations.append((class_id, [new_x_center, new_y_center, new_w, new_h]))
    
    return augmented_image, new_annotations

# Основной процесс аугментации
for label_file in tqdm(os.listdir(labels_dir), desc="Обработка аннотаций"):
    if label_file.endswith('.txt'):
        image_name = label_file.replace('.txt', '.png')  # Предполагается, что изображения имеют расширение .png
        image_path = os.path.join(images_dir, image_name)
        
        if not os.path.exists(image_path):
            continue
        
        annotations = read_yolo_annotations(os.path.join(labels_dir, label_file))

        for i in tqdm(range(augmentation_factor), desc=f"Аугментация {label_file}", leave=False):
            augmented_image, new_annotations = augment_image_and_annotations(image_path, annotations)
            # Сохранение аугментированного изображения только если есть новые аннотации
            if new_annotations:
                output_image_path = os.path.join(output_images_dir, f"{image_name.split('.')[0]}_aug_{i}.jpg")
                cv2.imwrite(output_image_path, augmented_image)

                # Сохранение новых аннотаций
                output_label_path = os.path.join(output_labels_dir, f"{label_file.split('.')[0]}_aug_{i}.txt")
                write_yolo_annotations(output_label_path, new_annotations)

print("Аугментация завершена.")
