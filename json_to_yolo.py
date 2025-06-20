#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 12:08:26 2025

@author: ann
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Конвертация JSON аннотаций в формат YOLO
"""

import os
import json
import argparse
from PIL import Image, ImageDraw, ImageFont

# Классы объектов (можно изменить под вашу задачу)
CLASSES = {
    "car": 0,
    "number": 1
}

def convert_to_yolo_format(bbox, img_width, img_height):
    """Конвертация bbox в формат YOLO (нормализованные координаты)"""
    x1, y1, x2, y2 = bbox
    
    # Расчет центра и размеров
    center_x = (x1 + x2) / 2 / img_width
    center_y = (y1 + y2) / 2 / img_height
    width = (x2 - x1) / img_width
    height = (y2 - y1) / img_height
    
    # Обеспечиваем, чтобы значения были в диапазоне [0, 1]
    center_x = max(0, min(1, center_x))
    center_y = max(0, min(1, center_y))
    width = max(0, min(1, width))
    height = max(0, min(1, height))
    
    return center_x, center_y, width, height

def process_json_to_yolo(json_path, img_width, img_height):
    """Обработка JSON файла и создание YOLO аннотаций"""
    yolo_lines = []
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Обработка обнаруженных объектов
    if 'detection' in data:
        detections = data['detection']
        
        # Обработка машин
        if 'car' in detections:
            for car in detections['car']:
                class_id = CLASSES["car"]
                cx, cy, w, h = convert_to_yolo_format(car['bbox'], img_width, img_height)
                yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
        
        # Обработка номеров
        if 'number' in detections:
            for number in detections['number']:
                class_id = CLASSES["number"]
                cx, cy, w, h = convert_to_yolo_format(number['bbox'], img_width, img_height)
                yolo_lines.append(f"{class_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    
    return yolo_lines

def process_folder(input_folder, output_folder):
    """Обработка всех файлов в папке"""
    os.makedirs(output_folder, exist_ok=True)
    files = os.listdir(input_folder)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    
    for image_file in image_files:
        json_file = image_file + '.json'
        
        if json_file in files:
            image_path = os.path.join(input_folder, image_file)
            json_path = os.path.join(input_folder, json_file)
            
            # Получаем размеры изображения
            with Image.open(image_path) as img:
                width, height = img.size
            
            # Создаем YOLO аннотации
            yolo_lines = process_json_to_yolo(json_path, width, height)
            
            # Сохраняем в файл
            output_file = os.path.splitext(image_file)[0] + '.txt'
            output_path = os.path.join(output_folder, output_file)
            
            with open(output_path, 'w') as f:
                f.write('\n'.join(yolo_lines))
            
            print(f"Processed {image_file} -> {output_file}")
        else:
            print(f"No JSON found for {image_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSON annotations to YOLO format.')
    parser.add_argument('input_folder', help='Path to the folder with images and JSON files')
    parser.add_argument('output_folder', help='Path to save YOLO annotation files')
    
    args = parser.parse_args()
    
    print(f"Converting annotations from {args.input_folder} to YOLO format...")
    process_folder(args.input_folder, args.output_folder)
    print("Conversion complete!")
    
    # Создаем файл classes.txt с именами классов
    classes_path = os.path.join(args.output_folder, "classes.txt")
    with open(classes_path, 'w') as f:
        for name, id in sorted(CLASSES.items(), key=lambda x: x[1]):
            f.write(f"{name}\n")
    
    print(f"Created {classes_path} with class names")