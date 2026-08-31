from django.core.management.base import BaseCommand
from django.db import connection
from final_project_app.models import Looks
import pandas as pd


class Command(BaseCommand):
    help = 'Import outfits from CSV to Looks model'

    def handle(self, *args, **options):
        # Удаляем все существующие записи
        Looks.objects.all().delete()

        # Сбрасываем последовательность ID для SQLite
        with connection.cursor() as cursor:
            try:
                cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='final_project_app_looks';")
            except:
                pass

        # Чтение CSV файла и импорт данных
        df = pd.read_csv('all_outfits_with_vectors.csv')

        for _, row in df.iterrows():
            # Преобразуем NaN в пустые строки
            data = {
                'temp_range': str(row.get('temp_range', '0_10')),
                'head': str(row.get('head', '')),
                'head_image': str(row.get('head_image', '')),
                'head_color': str(row.get('head_color', '')),
                'head_material': str(row.get('head_material', '')),
                'head_style': str(row.get('head_style', '')),
                'outerwear': str(row.get('outerwear', '')),
                'outerwear_image': str(row.get('outerwear_image', '')),
                'outerwear_color': str(row.get('outerwear_color', '')),
                'outerwear_material': str(row.get('outerwear_material', '')),
                'outerwear_style': str(row.get('outerwear_style', '')),
                'top': str(row.get('top', '')),
                'top_image': str(row.get('top_image', '')),
                'top_color': str(row.get('top_color', '')),
                'top_material': str(row.get('top_material', '')),
                'top_style': str(row.get('top_style', '')),
                'bottom': str(row.get('bottom', '')),
                'bottom_image': str(row.get('bottom_image', '')),
                'bottom_color': str(row.get('bottom_color', '')),
                'bottom_material': str(row.get('bottom_material', '')),
                'bottom_style': str(row.get('bottom_style', '')),
                'shoes': str(row.get('shoes', '')),
                'shoes_image': str(row.get('shoes_image', '')),
                'shoes_color': str(row.get('shoes_color', '')),
                'shoes_material': str(row.get('shoes_material', '')),
                'shoes_style': str(row.get('shoes_style', '')),
                'general_vector': str(row.get('general_vector', '')),
                'description': '',
                'style': 'classic'
            }
            
            # Заменяем 'nan' на пустые строки
            data = {k: ('' if v == 'nan' else v) for k, v in data.items()}
            
            Looks.objects.create(**data)

        count = Looks.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {count} образов'))
