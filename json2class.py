#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 12:11:59 2025

@author: ann
"""

import os
import requests
import json
import argparse
import yaml
import torch
from torchvision import transforms
from PIL import Image
import platform
import time
import shutil
from requests.exceptions import HTTPError, ChunkedEncodingError, ConnectionError, Timeout
from collections import defaultdict

# Обновленные классы, которые мы хотим сохранить
TARGET_CLASSES = {
    "ceiling_hatch",
    "driver_door_inside",
    "driver_seat",
    "driver_seat_adjustments",
    "engine_bay",
    "front",
    "front_left_3_4",
    "gearshift_switch_and_console",
    "instrument_cluster_and_steering_wheel",
    "interior_back_seat",
    "interior_through_driver_door",
    "interior_through_left_rear_door",
    "interior_through_right_front_door",
    "interior_through_right_rear_door",
    "media_screen",
    "mileage_and_instrument_panel_readings",
    "passenger_left_door_inside",
    "passenger_right_front_door_inside",
    "passenger_right_rear_door_inside",
    "passenger_seat",
    "rear",
    "rear_right_3_4",
    "side_left",
    "side_right",
    "steering_wheel_options",
    "trunk_inside",
    "vin",
    "wheel",
    "wheel_disk"
}

# Минимальная уверенность для сохранения изображения (80%)
MIN_CONFIDENCE = 0.8
# Максимальное количество изображений на класс
MAX_IMAGES_PER_CLASS = 500

def download_image(url, folder, filename, max_retries=3):
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    file_path = os.path.join(folder, filename)
    
    if os.path.exists(file_path):
        print(f"File already exists: {file_path}")
        return True  
    
    retries = 0
    while retries < max_retries:
        try:
            with requests.get(url, stream=True, timeout=10) as response:
                response.raise_for_status()
                
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        file.write(chunk)
                
                print(f"Downloaded: {file_path}")
                return True
        
        except HTTPError as http_err:
            if http_err.response.status_code == 404:
                print(f"HTTPError 404: Resource not found for URL: {url}")
                return False
            else:
                retries += 1
                print(f"HTTPError occurred: {http_err}. Retrying... Attempt {retries}/{max_retries}")
        
        except (ChunkedEncodingError, ConnectionError, Timeout) as e:
            retries += 1
            print(f"Attempt {retries}/{max_retries} failed for {url}. Error: {e}")
    
    print(f"Failed to download after {max_retries} attempts: {url}")
    return False

def load_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def classify_image(image_path, model, transform, class_names, device):
    image = Image.open(image_path).convert("RGB")
    image_tensor = transform(image).unsqueeze(0).to(device)

    start_time = time.time()

    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted_idx = torch.max(probabilities, 1)

    inference_time = time.time() - start_time
    predicted_class = class_names[predicted_idx.item()]
    confidence_score = confidence.item()

    return predicted_class, confidence_score, inference_time

def process_images(json_path, config_path, output_base_dir):
    # Загрузка конфигурации модели
    config = load_config(config_path)
    
    # Инициализация модели
    model_name = config["model"]["name"]
    weights_path = config["model"]["weights_path"]
    num_classes = config["model"]["num_classes"]

    # Инициализация EfficientNet-B0 с правильными параметрами
    model = torch.hub.load('pytorch/vision', 'efficientnet_b0', weights=None)
    in_features = model.classifier[1].in_features
    model.classifier[1] = torch.nn.Linear(in_features, num_classes)

    # Безопасная загрузка весов
    try:
        state_dict = torch.load(weights_path, map_location=torch.device('cpu'), weights_only=True)
        model.load_state_dict(state_dict)
    except Exception as e:
        print(f"Error loading model weights: {e}")
        return

    model.eval()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    class_names = config["classes"]
    transform = transforms.Compose([
        transforms.Resize(tuple(config["image_size"])),
        transforms.ToTensor(),
        transforms.Normalize(mean=config["mean"], std=config["std"])
    ])

    # Загрузка JSON данных
    try:
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return

    # Инициализация счетчиков
    class_counts = defaultdict(int)
    stats = {
        'downloaded': 0,
        'classified': 0,
        'skipped': 0,
        'low_confidence': 0,
        'limit_reached': 0
    }

    # Создаем временную папку
    temp_folder = "temp_images"
    os.makedirs(temp_folder, exist_ok=True)

    # Обработка изображений
    for item in data:
        # Проверяем наличие необходимых полей
        if not all(key in item for key in ['model', 'angle_type', 'url']):
            stats['skipped'] += 1
            continue

        url = item['url']
        filename = os.path.basename(url)
        temp_path = os.path.join(temp_folder, filename)

        # Скачивание изображения
        if not download_image(url, temp_folder, filename):
            stats['skipped'] += 1
            continue
        stats['downloaded'] += 1

        # Классификация
        try:
            predicted_class, confidence_score, _ = classify_image(
                temp_path, model, transform, class_names, device
            )
            
            print(f"Processing: {filename} -> {predicted_class} ({confidence_score:.2f})")

            # Проверка условий сохранения
            if predicted_class.lower() not in TARGET_CLASSES:
                stats['skipped'] += 1
            elif confidence_score < MIN_CONFIDENCE:
                stats['low_confidence'] += 1
            elif class_counts[predicted_class.lower()] >= MAX_IMAGES_PER_CLASS:
                stats['limit_reached'] += 1
            else:
                # Сохранение изображения
                class_folder = os.path.join(output_base_dir, predicted_class.lower())
                os.makedirs(class_folder, exist_ok=True)
                shutil.copy2(temp_path, os.path.join(class_folder, filename))
                
                class_counts[predicted_class.lower()] += 1
                stats['classified'] += 1

        except Exception as e:
            print(f"Error processing {filename}: {e}")
            stats['skipped'] += 1
        finally:
            # Удаление временного файла
            if os.path.exists(temp_path):
                os.remove(temp_path)

        # Проверка лимитов - только если для ВСЕХ классов достигнут лимит
        if all(class_counts.get(cls.lower(), 0) >= MAX_IMAGES_PER_CLASS for cls in TARGET_CLASSES):
            print("Reached maximum images limit for all target classes.")
            break

    # Удаление временной папки
    shutil.rmtree(temp_folder, ignore_errors=True)

    # Вывод статистики
    print("\nProcessing results:")
    print(f"Total images processed: {len(data)}")
    print(f"Successfully downloaded: {stats['downloaded']}")
    print(f"Classified to target classes: {stats['classified']}")
    print(f"Skipped (low confidence): {stats['low_confidence']}")
    print(f"Skipped (class limit reached): {stats['limit_reached']}")
    print(f"Skipped (other reasons): {stats['skipped']}")
    
    print("\nImages per class:")
    for cls in sorted(TARGET_CLASSES):
        print(f"{cls}: {class_counts.get(cls, 0)}/{MAX_IMAGES_PER_CLASS}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and classify car images.")
    parser.add_argument("--json", type=str, required=True, help="Path to the JSON file with image URLs")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to the model configuration file")
    parser.add_argument("--output", type=str, default="classified_images", help="Base directory for classified images")
    parser.add_argument("--min_confidence", type=float, default=0.8, 
                       help="Minimum confidence threshold for saving images (default: 0.8)")
    parser.add_argument("--max_images", type=int, default=500,
                       help="Maximum number of images to save per class (default: 500)")
    
    args = parser.parse_args()
    
    # Обновляем параметры из аргументов командной строки
    MIN_CONFIDENCE = args.min_confidence
    MAX_IMAGES_PER_CLASS = args.max_images
    
    process_images(args.json, args.config, args.output)