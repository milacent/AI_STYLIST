import subprocess
import sys
import os
from django.core.management.base import BaseCommand
from concurrent.futures import ThreadPoolExecutor


class Command(BaseCommand):
    help = 'Запускает Django и Flask сервера одновременно'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Запуск Django и Flask серверов...'))

        # Путь к manage.py (в корне проекта)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        django_manage_path = os.path.join(project_root, "manage.py")

        # Путь к Flask app.py
        flask_app_path = os.path.join(project_root, "final_project_app", "flask", "app.py")

        def run_django():
            self.stdout.write(self.style.HTTP_INFO("🌐 Запуск Django на порту 8000"))
            subprocess.run([sys.executable, "manage.py", "runserver", "8000"], cwd=project_root)

        def run_flask():
            if not os.path.exists(flask_app_path):
                self.stdout.write(self.style.ERROR(f"❌ Не найден файл Flask: {flask_app_path}"))
                return

            flask_dir = os.path.dirname(flask_app_path)
            self.stdout.write(self.style.HTTP_INFO(f"🧪 Запуск Flask из: {flask_app_path}"))
            subprocess.run([sys.executable, "app.py"], cwd=flask_dir)

        try:
            with ThreadPoolExecutor() as executor:
                executor.submit(run_django)
                executor.submit(run_flask)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Оба сервера остановлены пользователем."))
            sys.exit(0)