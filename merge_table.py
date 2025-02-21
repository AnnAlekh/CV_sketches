#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 21 12:02:01 2025

@author: ann
"""

import os
import pandas as pd

# Укажите путь к папке с файлами
folder_path = '/media/ann/UBUNTU 24_0/expert_mark'

# Создаем пустой DataFrame для хранения результатов
result_df = pd.DataFrame(columns=['Название картинки'])

# Проходим по всем файлам в папке
for file_name in os.listdir(folder_path):
    if file_name.endswith('.xlsx') or file_name.endswith('.xls'):
        file_path = os.path.join(folder_path, file_name)
        
        # Читаем файл
        df = pd.read_excel(file_path)
        
        # Проверяем, есть ли в файле столбец "участник_2"
        if 'участник_2' not in df.columns:
            print(f"В файле {file_name} отсутствует столбец 'участник_2'. Пропускаем файл.")
            continue
        
        # Проходим по каждой строке в файле
        for index, row in df.iterrows():
            image_name = row['Название картинки']
            rating = row['участник_2']
            
            # Пропускаем пустые строки (если название картинки отсутствует)
            if pd.isna(image_name):
                continue
            
            # Проверяем, есть ли уже это изображение в итоговом DataFrame
            if image_name in result_df['Название картинки'].values:
                # Если изображение уже есть, добавляем оценку в следующий столбец
                idx = result_df.index[result_df['Название картинки'] == image_name].tolist()[0]
                
                # Ищем последний заполненный столбец для этого изображения
                last_col = 1
                while f'Участник {last_col}' in result_df.columns and not pd.isna(result_df.at[idx, f'Участник {last_col}']):
                    last_col += 1
                
                # Если столбца еще нет, добавляем его
                if f'Участник {last_col}' not in result_df.columns:
                    result_df[f'Участник {last_col}'] = None
                
                # Записываем оценку
                result_df.at[idx, f'Участник {last_col}'] = rating
            else:
                # Если изображения нет, добавляем новую строку
                new_row = pd.DataFrame({'Название картинки': [image_name], 'Участник 1': [rating]})
                result_df = pd.concat([result_df, new_row], ignore_index=True)

# Сохраняем результат в новый Excel-файл
result_df.to_excel('общий_файл.xlsx', index=False)