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
            cursor.execute("UPDATE sqlite_sequence SET seq=0 WHERE name='final_project_app_looks';")

        # Чтение CSV файла и импорт данных
        df = pd.read_csv('all_outfits_with_vectors.csv')
        outfits = df.to_dict('records')

        for outfit in outfits:
            outfit.pop('id', None)
            Looks.objects.create(**outfit)

        self.stdout.write(self.style.SUCCESS(f'Успешно импортировано {len(outfits)} образов'))
