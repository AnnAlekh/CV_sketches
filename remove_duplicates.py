#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 23 12:12:04 2025

@author: ann
"""

#!/usr/bin/env python3
import os
import hashlib
from collections import defaultdict

def find_duplicate_images(folder):
    # Словарь для хранения хешей и соответствующих файлов
    hash_dict = defaultdict(list)
    
    # Перебираем все файлы в папке
    for filename in os.listdir(folder):
        filepath = os.path.join(folder, filename)
        
        # Проверяем, что это файл (не папка) и это изображение
        if os.path.isfile(filepath) and filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            # Вычисляем хеш содержимого файла
            with open(filepath, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            # Добавляем в словарь
            hash_dict[file_hash].append(filepath)
    
    # Возвращаем только дубликаты (где количество файлов с одним хешем > 1)
    return {h: files for h, files in hash_dict.items() if len(files) > 1}

def delete_duplicates(folder, keep_first=True):
    # Находим дубликаты
    duplicates = find_duplicate_images(folder)
    
    if not duplicates:
        print("Дубликаты не найдены.")
        return
    
    print(f"Найдено {len(duplicates)} групп дубликатов.")
    
    # Удаляем дубликаты
    deleted_count = 0
    for hash_val, files in duplicates.items():
        # Сортируем файлы для детерминированного выбора
        files.sort()
        
        # Определяем какие файлы удалять (оставляем первый или последний)
        to_delete = files[1:] if keep_first else files[:-1]
        
        # Удаляем файлы
        for filepath in to_delete:
            try:
                os.remove(filepath)
                print(f"Удален дубликат: {filepath}")
                deleted_count += 1
            except Exception as e:
                print(f"Ошибка при удалении {filepath}: {e}")
    
    print(f"Удалено {deleted_count} файлов-дубликатов.")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Удаление одинаковых изображений в папке')
    parser.add_argument('folder', help='Путь к папке с изображениями')
    parser.add_argument('--keep-last', action='store_true', 
                       help='Оставлять последний дубликат вместо первого')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.folder):
        print("Ошибка: указанная папка не существует.")
        exit(1)
    
    print(f"Поиск дубликатов в папке: {args.folder}")
    delete_duplicates(args.folder, keep_first=not args.keep_last)