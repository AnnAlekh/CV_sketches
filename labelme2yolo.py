import os
import json
from glob import glob

def convert_labelme_to_yolo(json_dir, output_dir, class_mapping):
    os.makedirs(output_dir, exist_ok=True)

    json_files = glob(os.path.join(json_dir, "*.json"))

    for json_path in json_files:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        image_width = data.get('imageWidth')
        image_height = data.get('imageHeight')

        if not image_width or not image_height:
            print(f"Missing image dimensions in {json_path}")
            continue

        base_name = os.path.splitext(os.path.basename(json_path))[0]
        output_path = os.path.join(output_dir, base_name + '.txt')

        with open(output_path, 'w', encoding='utf-8') as out_f:
            for shape in data['shapes']:
                label = shape['label']
                points = shape['points']
                shape_type = shape['shape_type']

                if shape_type != 'polygon':
                    print(f"Skipping non-polygon shape in {json_path}: {shape_type}")
                    continue

                if label not in class_mapping:
                    raise ValueError(f"Class '{label}' not found in class_mapping.")

                class_id = class_mapping[label]

                normalized_points = []
                for x, y in points:
                    xn = x / image_width
                    yn = y / image_height
                    normalized_points.append((xn, yn))

                line = str(class_id) + " " + " ".join(f"{x:.6f} {y:.6f}" for x, y in normalized_points)
                out_f.write(line + '\n')


# === НАСТРОЙКИ ===
json_dir = '/home/ann/script/1/sausage, pasta, soup/'              # Папка с JSON-файлами
output_dir = '/home/ann/script/1/sausage, pasta, soup/yolo_labels'            # Папка для сохранения .txt
class_mapping = {
    "sausage": 0,
    'pasta': 1,
    'soup' : 2
    # Добавьте другие классы здесь
}

# === ЗАПУСК КОНВЕРТАЦИИ ===
convert_labelme_to_yolo(json_dir, output_dir, class_mapping)
print("✅ Конвертация завершена!")