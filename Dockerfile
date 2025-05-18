FROM python:3.11

WORKDIR /mshp-final-project-meow

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000
EXPOSE 5000

CMD ["sh", "-c", "cd final_project  && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 final_project.wsgi:application"]
