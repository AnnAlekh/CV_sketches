#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 15:27:18 2025

@author: ann
"""

import os

# Пути к папкам с разметкой
label_folder = "/home/ann/Загрузки/License Plates Recognition.v2i.yolov8/train/labels"  # Папка с исходной разметкой
label1_folder = "/home/ann/Загрузки/License Plates Recognition.v2i.yolov8/train/label1"  # Папка, куда нужно добавить измененную разметку

# Создаем папку label1, если она не существует
os.makedirs(label1_folder, exist_ok=True)

# Проходим по всем файлам в папке label
for label_file_name in os.listdir(label_folder):
    if not label_file_name.endswith(".txt"):
        continue

    # Полный путь к файлу в папке label
    label_file_path = os.path.join(label_folder, label_file_name)
    
    # Полный путь к файлу в папке label1
    label1_file_path = os.path.join(label1_folder, label_file_name)

    # Читаем содержимое файла из папки label
    with open(label_file_path, "r") as label_file:
        lines = label_file.readlines()

    # Заменяем класс 0 на класс 1
    new_lines = []
    for line in lines:
        parts = line.strip().split()
        if parts[0] == "0":  # Если класс равен 0
            parts[0] = "1"   # Заменяем на 1
        new_lines.append(" ".join(parts) + "\n")

    # Если файл в папке label1 уже существует, добавляем новую разметку к существующей
    if os.path.exists(label1_file_path):
        with open(label1_file_path, "r") as label1_file:
            existing_lines = label1_file.readlines()
        new_lines = existing_lines + new_lines

    # Записываем измененную разметку в файл в папке label1
    with open(label1_file_path, "w") as label1_file:
        label1_file.writelines(new_lines)

print("Обработка завершена.")