# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import cv2

# Путь к папке с исходными изображениями
input_dir = "/home/ann/Загрузки/Данныетестов/result/output/image"

# Путь к папке для сохранения новых изображений
output_dir = "/home/ann/Загрузки/Данныетестов/result/output/split_images"
os.makedirs(output_dir, exist_ok=True)

# Функция для разбиения изображения пополам
def split_image(image):
    height, width, _ = image.shape
    left_half = image[:, :width // 2, :]
    right_half = image[:, width // 2:, :]
    return left_half, right_half

# Проходим по всем файлам в указанной директории
for filename in os.listdir(input_dir):
    if filename.endswith(".png") or filename.endswith(".jpg"):
        # Полный путь к исходному изображению
        input_path = os.path.join(input_dir, filename)
        
        # Чтение изображения
        image = cv2.imread(input_path)
        
        # Проверка размера изображения
        if image is not None and image.shape[1] == 3840 and image.shape[0] == 1080:
            # Разбиваем изображение на две части
            left_half, right_half = split_image(image)
            
            # Формируем новые имена файлов
            base_name = os.path.splitext(filename)[0]
            left_output_path = os.path.join(output_dir, f"{base_name}_left.png")
            right_output_path = os.path.join(output_dir, f"{base_name}_right.png")
            
            # Сохраняем новые изображения
            cv2.imwrite(left_output_path, left_half)
            cv2.imwrite(right_output_path, right_half)
            print(f"Processed {filename} -> {left_output_path}, {right_output_path}")
        else:
            print(f"Skipping {filename} (invalid size)")

print("All images processed.")