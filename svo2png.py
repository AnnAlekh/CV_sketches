#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 19 14:43:04 2025

@author: ann
"""

import pyzed.sl as sl

def svo_to_png(svo_file, output_dir):
    # Инициализация объекта для чтения SVO
    zed = sl.Camera()
    init_params = sl.InitParameters()
    init_params.set_from_svo_file(svo_file)
    init_params.svo_real_time_mode = False  # Отключаем реальное время для полного контроля
    
    # Открытие SVO-файла
    err = zed.open(init_params)
    if err != sl.ERROR_CODE.SUCCESS:
        print(f"Ошибка открытия SVO: {err}")
        return
    
    # Получение количества кадров
    nb_frames = zed.get_svo_number_of_frames()
    print(f"Всего кадров: {nb_frames}")
    
    # Создание изображений для сохранения
    left_image = sl.Mat()
    right_image = sl.Mat()
    
    # Извлечение кадров
    for i in range(nb_frames):
        if zed.grab() == sl.ERROR_CODE.SUCCESS:
            zed.retrieve_image(left_image, sl.VIEW.LEFT)  # Левый кадр
            zed.retrieve_image(right_image, sl.VIEW.RIGHT)  # Правый кадр (опционально)
            
            # Сохранение в PNG
            left_image.write(f"{output_dir}/left_{i:04d}.png")
            # right_image.write(f"{output_dir}/right_{i:04d}.png")  # Если нужно сохранить оба кадра
            
            print(f"Сохранен кадр {i + 1}/{nb_frames}")
    
    zed.close()
    print("Готово!")

# Пример вызова
svo_to_png("/home/ann/Загрузки/archive-2025-05-19_09-37-45/archive/HD720_SN24943460_20-11-48.svo", "2")