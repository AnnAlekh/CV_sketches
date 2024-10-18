#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 10:57:51 2024

@author: ann
"""

import os
import matplotlib.pyplot as plt

def count_files_in_folders(source_folder):
    folder_counts = {}

    # Проходим по всем элементам в указанной директории
    for item in os.listdir(source_folder):
        item_path = os.path.join(source_folder, item)
        if os.path.isdir(item_path):  # Проверяем, является ли элемент папкой
            file_count = len([f for f in os.listdir(item_path) if os.path.isfile(os.path.join(item_path, f))])
            folder_counts[item] = file_count

    return folder_counts

def plot_file_counts(folder_counts):
    folders = list(folder_counts.keys())
    counts = list(folder_counts.values())

    plt.figure(figsize=(12, 8))  # Увеличиваем размер графика
    plt.bar(folders, counts, color='lightcoral')
    plt.xlabel('Класс', fontsize=14)
    plt.ylabel('Количество образцов', fontsize=14)
    plt.title('Распределение образцов на класс', fontsize=16)
    plt.xticks(rotation=45, ha='right', fontsize=10)  # Поворачиваем подписи и выравниваем их
    plt.tight_layout()
    plt.savefig('folder_file_counts.png')
    plt.show()

if __name__ == "__main__":  # Исправлено: должно быть "__name__" и "__main__"
    source_folder = '/home/ann/Distortion classification/NUS_WIDE_noise'
    
    folder_counts = count_files_in_folders(source_folder)
    plot_file_counts(folder_counts)
