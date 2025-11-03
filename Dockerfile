# base python
FROM python:3.11-slim

# variables de entorno
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# copiar código
COPY . /app/

# collectstatic si usas staticfiles (opcional)
# RUN python manage.py collectstatic --noinput

# puerto
EXPOSE 8080

# comando de arranque (Gunicorn)
CMD ["gunicorn", "nombre_proyecto.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]