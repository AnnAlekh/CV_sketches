import os
import cv2
from ultralytics import YOLO

# Загрузка обученной модели YOLOv8
model = YOLO("/home/ann/Загрузки/Telegram Desktop/runs/detect/train/weights/CAR_NUMBERbest.pt")

# Папки для ввода/вывода
input_videos_dir = "/home/ann/Загрузки/13 июня/1"
output_frames_dir = "/home/ann/Загрузки/CAR_NUMBER/img"
output_labels_dir = "/home/ann/Загрузки/CAR_NUMBER/labels"

# Создание папок, если их нет
os.makedirs(output_frames_dir, exist_ok=True)
os.makedirs(output_labels_dir, exist_ok=True)

# Обработка каждого видео
for video_file in os.listdir(input_videos_dir):
    if not video_file.endswith((".mp4", ".avi", ".mov")):
        continue

    video_path = os.path.join(input_videos_dir, video_file)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Детекция объектов
        results = model(frame, verbose=False)
        boxes = results[0].boxes.xywhn.cpu().numpy()  # Нормализованные координаты
        classes = results[0].boxes.cls.cpu().numpy()  # Классы

        # Если есть детекции (хотя бы один объект)
        if len(boxes) > 0:
            # Сохранение кадра
            frame_filename = f"{os.path.splitext(video_file)[0]}_{frame_count:04d}.jpg"
            frame_path = os.path.join(output_frames_dir, frame_filename)
            cv2.imwrite(frame_path, frame)

            # Сохранение аннотаций YOLO
            label_filename = f"{os.path.splitext(video_file)[0]}_{frame_count:04d}.txt"
            label_path = os.path.join(output_labels_dir, label_filename)

            with open(label_path, "w") as f:
                for box, cls in zip(boxes, classes):
                    x_center, y_center, width, height = box
                    f.write(f"{int(cls)} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        frame_count += 1

    cap.release()
    print(f"Обработано видео: {video_file}, сохранено кадров с детекциями: {len(os.listdir(output_frames_dir))}")