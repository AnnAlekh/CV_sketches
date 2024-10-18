import os
import shutil
import sys

def sort_files(source_folder):
    # Получаем список файлов в указанной директории
    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]

    # Словарь для группировки файлов по префиксам
    file_groups = {}

    # Группируем файлы по префиксам
    for file in files:
        # Используем часть имени файла до первого символа "_" как префикс
        prefix = file.split('_')[0]  # Измените разделитель по необходимости
        if prefix not in file_groups:
            file_groups[prefix] = []
        file_groups[prefix].append(file)

    # Создаем папки и перемещаем файлы
    for prefix, grouped_files in file_groups.items():
        # Создаем директорию с именем префикса, если она не существует
        prefix_path = os.path.join(source_folder, prefix)
        if not os.path.exists(prefix_path):
            os.makedirs(prefix_path)
        
        # Перемещаем файлы в соответствующую папку
        for file in grouped_files:
            shutil.move(os.path.join(source_folder, file), os.path.join(prefix_path, file))

    print("Файлы успешно отсортированы по папкам.")

if __name__ == "__main__":

    source_folder = '/home/ann/SibGU/NEW_CLASS/data/data_find_casei'
    
    sort_files(source_folder)
