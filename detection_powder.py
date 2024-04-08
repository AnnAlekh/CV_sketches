#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 15:32:38 2024

@author: anna
"""

import cv2

# Загрузка видео
cap = cv2.VideoCapture('/home/anna/detection_powder/1.avi')

# Инициализация метода вычитания фона
fgbg = cv2.createBackgroundSubtractorMOG2()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Применение метода вычитания фона
    fgmask = fgbg.apply(frame)

    # Применение морфологических операций для улучшения результатов
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

    # Поиск контуров движущихся объектов
    contours, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        # Отфильтровываем небольшие контуры
        if cv2.contourArea(contour) < 10:
            continue

        # Отрисовываем прямоугольник вокруг контура
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('Motion Detection', frame)

    if cv2.waitKey(30) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()