#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 16:49:57 2025

@author: ann
"""

import os
import random
import shutil
from PIL import Image

# Пути к исходным папкам
source_dir_front_left = '/home/ann/CAR_EDIT_DATASET/DATASET/train/front_left_3_4'
source_dir_rear_right = '/home/ann/CAR_EDIT_DATASET/DATASET/train/rear_right_3_4'

# Целевая папка для сохранения синтетических данных
target_base_dir = 'SINT_NOISE'

os.makedirs(target_base_dir, exist_ok=True)

def flip_and_save_images(source_dir, target_subdir, percentage=0.2):
    # Создаем целевую подпапку
    target_dir = os.path.join(target_base_dir, target_subdir)
    os.makedirs(target_dir, exist_ok=True)

    # Получаем список всех изображений в исходной папке
    all_images = [f for f in os.listdir(source_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    num_to_process = int(len(all_images) * percentage)

    print(f"Processing {num_to_process} images from {source_dir}...")

    # Выбираем случайные 20%
    selected_images = random.sample(all_images, num_to_process)

    for img_name in selected_images:
        src_path = os.path.join(source_dir, img_name)
        dst_path = os.path.join(target_dir, img_name)

        try:
            with Image.open(src_path) as img:
                img = img.convert('RGB')  # Убедиться, что RGB
                flipped_img = img.transpose(Image.FLIP_LEFT_RIGHT)  # Горизонтальное отражение
                flipped_img.save(dst_path)  # Сохраняем в новое место
        except Exception as e:
            print(f"Ошибка при обработке {img_name}: {e}")

    print(f"Сохранено {num_to_process} изображений в {target_dir}")

if __name__ == '__main__':
    # Обрабатываем front_left_3_4
    flip_and_save_images(
        source_dir=source_dir_front_left,
        target_subdir='front_left_flipped',
        percentage=0.5
    )

    # Обрабатываем rear_right_3_4
    flip_and_save_images(
        source_dir=source_dir_rear_right,
        target_subdir='rear_right_flipped',
        percentage=0.5
    )

    print("Горизонтальное отражение успешно выполнено и сохранено в SINT_NOISE")