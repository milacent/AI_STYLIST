import subprocess
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Запускает Flask сервер'

    def handle(self, *args, **kwargs):
        flask_app_path = 'myflask/app.py'  # Путь до вашего Flask-файла
        self.stdout.write(self.style.SUCCESS('Запускаем Flask сервер...'))
        try:
            subprocess.run(['python', flask_app_path], check=True)
        except subprocess.CalledProcessError as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при запуске Flask: {e}'))