import os
import cv2
import numpy as np
import matplotlib.pyplot as plt
from brisque import BRISQUE
from tqdm import tqdm

# Путь к папке с данными
base_path = "/home/ann/CAR_EDIT_DATASET/DATASET/train/"

# Инициализация BRISQUE
brisque = BRISQUE()

# Словарь для хранения результатов
results = {}

# Получаем список папок для обработки
folders_to_process = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
total_folders = len(folders_to_process)

# Обработка каждой папки с прогресс-баром
print("Обработка папок с изображениями:")
for folder_name in tqdm(folders_to_process, desc="Папки", unit="папка"):
    folder_path = os.path.join(base_path, folder_name)
    scores = []
    
    # Получаем список изображений
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    # Обработка каждого изображения в папке с вложенным прогресс-баром
    for img_name in tqdm(image_files, desc=f"Изображения в {folder_name}", leave=False, unit="img"):
        img_path = os.path.join(folder_path, img_name)
        try:
            img = cv2.imread(img_path)
            if img is not None:
                score = brisque.score(img)
                scores.append(score)
        except Exception as e:
            print(f"\nОшибка при обработке {img_path}: {e}")
    
    # Сохраняем результаты для папки
    if scores:
        results[folder_name] = scores

# Подготовка данных для диаграммы
all_scores = []
for folder, scores in results.items():
    all_scores.extend(scores)

# Создание гистограммы
print("\nСоздание диаграммы...")
plt.figure(figsize=(12, 6))
plt.hist(all_scores, bins=30, color='blue', alpha=0.7)
plt.title('Распределение оценок BRISQUE по всем изображениям')
plt.xlabel('Оценка BRISQUE (чем выше - тем хуже качество)')
plt.ylabel('Количество изображений')
plt.grid(True)

# Сохранение диаграммы
output_path = os.path.join(base_path, 'brisque_distribution.png')
plt.savefig(output_path)
plt.close()

print(f"\nДиаграмма сохранена в {output_path}")
print("\nСтатистика по оценкам BRISQUE:")
print(f"Всего изображений: {len(all_scores)}")
print(f"Средняя оценка: {np.mean(all_scores):.2f}")
print(f"Медианная оценка: {np.median(all_scores):.2f}")
print(f"Минимальная оценка: {np.min(all_scores):.2f}")
print(f"Максимальная оценка: {np.max(all_scores):.2f}")