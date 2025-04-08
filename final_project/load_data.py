import os
from final_project_app.models import *


def load_clothes():
    categories = {
        'head': 'head',
        'outerwear': 'outerwear',
        'tops': 'tops',
        'bottoms': 'bottoms',
        'shoes': 'shoes'
    }

    temp_ranges = [
        ('-20_-10', -20, -10),
        ('-10_0', -10, 0),
        ('0_10', 0, 10),
        ('10_20', 10, 20),
        ('20_30', 20, 30)
    ]

    for cat_code, cat_name in categories.items():
        # Путь к папке категории
        category_folder = os.path.join('final_project_app', 'static', 'images', 'default_clothes', cat_name)

        if not os.path.exists(category_folder):
            print(f"Папка не найдена: {category_folder}")
            continue

        # Обрабатываем каждую температурную папку
        for temp_folder, min_temp, max_temp in temp_ranges:
            temp_folder_path = os.path.join(category_folder, temp_folder)

            # Проверяем существование температурной папки
            if not os.path.exists(temp_folder_path):
                print(f"Температурная папка не найдена: {temp_folder_path}")
                continue

            # Обрабатываем файлы в папке
            for filename in os.listdir(temp_folder_path):
                if filename.lower().endswith('.png'):
                    name = os.path.splitext(filename)[0]
                    ClothingItem.objects.create(
                        category=cat_code,
                        name=name,
                        image_name=filename,
                        min_temp=min_temp,
                        max_temp=max_temp,
                        color = "black",
                        style = "classic",
                        material="cotton"
                    )
                    print(f"Добавлен: {cat_code} - {name} ({min_temp}..{max_temp}°C)")


if __name__ == '__main__':
    load_clothes()