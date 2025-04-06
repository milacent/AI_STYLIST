import os
from final_project_app.models import ClothingItem

def load_clothes():
    categories= [
        ('hats', 'Головные уборы'),
        ('outerwear', 'Верхняя одежда'),
        ('tops', 'Топы'),
        ('bottoms', 'Низы'),
        ('shoes', 'Обувь')
    ]

    for cat_code, cat_folder in categories.items():
        folder_path = os.path.join('final_project_app', 'static', 'images', 'default_clothes', cat_folder)

        for filename in os.listdir(folder_path):
            if filename.endswith('.png'):
                name = filename.split('.')[0]
                ClothingItem.objects.create(
                    category=cat_code,
                    name=name,
                    image_name=filename,
                    min_temp=-20,
                    max_temp=30
                )