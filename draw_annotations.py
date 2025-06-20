#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 11:39:36 2025

@author: ann
"""

import os
import json
from PIL import Image, ImageDraw, ImageFont

# ============================================
# ПУТИ (измените эти значения на свои)
# ============================================
INPUT_FOLDER = "/home/ann/CAR_NUMBER_JSON"
OUTPUT_FOLDER = "/home/ann/CAR_NUMBER_JSON/out"
CROP_NUMBER_DIR = "/home/ann/CAR_NUMBER_JSON/crop_number"
YOLO_LABELS_DIR = "/home/ann/CAR_NUMBER_JSON/YOLO_labels"
# ============================================

def process_image(image_path, json_path, output_path):
    # Загрузка оригинального изображения (без рисования)
    orig_image = Image.open(image_path)
    width, height = orig_image.size
    
    # Создаем копию для рисования bounding boxes
    draw_image = orig_image.copy()
    draw = ImageDraw.Draw(draw_image)
    
    try:
        # Загрузка JSON данных
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        # Функция для отрисовки bounding box (только на draw_image)
        def draw_bbox(bbox, color, label=None, confidence=None):
            x1 = max(0, min(width, bbox[0]))
            y1 = max(0, min(height, bbox[1]))
            x2 = max(0, min(width, bbox[2]))
            y2 = max(0, min(height, bbox[3]))
            
            draw.rectangle([x1, y1, x2, y2], outline=color, width=3)
            
            if label and confidence:
                text = f"{label} {confidence:.2f}"
                font = ImageFont.load_default()
                left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                text_width, text_height = right - left, bottom - top
                
                text_y = max(0, y1 - text_height - 5)
                draw.rectangle([x1, text_y, x1 + text_width + 5, text_y + text_height], fill=color)
                draw.text((x1 + 2, text_y), text, fill="white", font=font)
        
        # Подготовка данных для YOLO разметки
        yolo_lines = []
        
        if 'detection' in data:
            detections = data['detection']
            
            # Обработка машин (синий цвет)
            if 'car' in detections:
                for car in detections['car']:
                    bbox = car['bbox']
                    draw_bbox(bbox, color='blue', label='car', confidence=car['confidence'])
                    # Конвертация в YOLO формат
                    x_center = (bbox[0] + bbox[2]) / 2 / width
                    y_center = (bbox[1] + bbox[3]) / 2 / height
                    bbox_width = (bbox[2] - bbox[0]) / width
                    bbox_height = (bbox[3] - bbox[1]) / height
                    yolo_lines.append(f"0 {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}")
            
            # Обработка номеров (зеленый цвет)
            if 'number' in detections:
                for i, number in enumerate(detections['number']):
                    bbox = number['bbox']
                    draw_bbox(bbox, color='green', label='number', confidence=number['confidence'])
                    # Конвертация в YOLO формат
                    x_center = (bbox[0] + bbox[2]) / 2 / width
                    y_center = (bbox[1] + bbox[3]) / 2 / height
                    bbox_width = (bbox[2] - bbox[0]) / width
                    bbox_height = (bbox[3] - bbox[1]) / height
                    yolo_lines.append(f"1 {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}")
                    
                    # Получаем распознанный номер из данных OCR
                    recognized_number = data.get('result_number', f"unknown_{i}")
                    
                    # Создаем папку для этого номера
                    number_dir = os.path.join(CROP_NUMBER_DIR, recognized_number)
                    os.makedirs(number_dir, exist_ok=True)
                    
                    # Вырезание области номера из ОРИГИНАЛЬНОГО изображения (без рамок)
                    cropped = orig_image.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
                    
                    # Генерируем уникальное имя файла
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    crop_filename = f"{base_name}_number_{i}.jpg"
                    crop_path = os.path.join(number_dir, crop_filename)
                    
                    # Сохраняем изображение
                    cropped.save(crop_path)
        
        # Отрисовка целевого bbox и результата OCR (красный цвет)
        if 'target_bbox' in data:
            target_bbox = data['target_bbox']
            draw_bbox(target_bbox, color='red', label='target')
            
            if 'ocr' in data and 'result_number' in data:
                x1, y1, x2, y2 = target_bbox
                text = f"OCR: {data['ocr']} | Result: {data['result_number']}"
                font = ImageFont.load_default()
                left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
                text_width, text_height = right - left, bottom - top
                
                text_y = min(height, y2 + 5)
                text_x = max(0, min(x1, width - text_width - 10))
                
                draw.rectangle([text_x, text_y, text_x + text_width + 10, text_y + text_height + 5], fill='red')
                draw.text((text_x + 5, text_y + 2), text, fill="white", font=font)
        
        # Сохранение YOLO разметки
        yolo_filename = os.path.splitext(os.path.basename(image_path))[0] + ".txt"
        with open(os.path.join(YOLO_LABELS_DIR, yolo_filename), 'w') as f:
            f.write("\n".join(yolo_lines))
    
    except Exception as e:
        print(f"Error processing {json_path}: {str(e)}")
    
    # Сохранение изображения с bounding boxes
    draw_image.save(output_path)

def process_folder():
    # Создание выходных папок
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    os.makedirs(CROP_NUMBER_DIR, exist_ok=True)
    os.makedirs(YOLO_LABELS_DIR, exist_ok=True)
    
    # Сбор всех файлов в папке
    files = os.listdir(INPUT_FOLDER)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    
    for image_file in image_files:
        # Определение соответствующих JSON файлов
        json_file = image_file + '.json'
        
        if json_file in files:
            # Полные пути к файлам
            image_path = os.path.join(INPUT_FOLDER, image_file)
            json_path = os.path.join(INPUT_FOLDER, json_file)
            output_path = os.path.join(OUTPUT_FOLDER, image_file)
            
            # Обработка и сохранение
            print(f"Processing {image_file} with {json_file}...")
            process_image(image_path, json_path, output_path)
        else:
            print(f"No JSON found for {image_file}")

if __name__ == "__main__":
    print(f"Input folder: {INPUT_FOLDER}")
    print(f"Output folder: {OUTPUT_FOLDER}")
    print(f"Crop number dir: {CROP_NUMBER_DIR}")
    print(f"YOLO labels dir: {YOLO_LABELS_DIR}")
    
    process_folder()
    print("Processing complete!")