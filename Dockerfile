# Base Python
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=Barrovivo.settings
ENV ALLOWED_HOSTS="*"
ENV DEBUG=False

WORKDIR /app

# Instalar dependencias del sistema necesarias para Cairo, Django, PDF, imágenes, etc. + NGINX
RUN apt-get update -y && apt-get install -y \
    gcc \
    libcairo2-dev \
    libpango1.0-dev \
    libjpeg-dev \
    zlib1g-dev \
    libffi-dev \
    libxml2 \
    libxml2-dev \
    libxslt1-dev \
    libssl-dev \
    build-essential \
    nginx \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip cache purge

# Copiar el proyecto
COPY . /app/

# Recolectar archivos estáticos
RUN python manage.py collectstatic --noinput

# Copiar configuración de Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponer puerto
EXPOSE 80

# Arranque de Nginx + Gunicorn
CMD service nginx start && \
    gunicorn Barrovivo.wsgi:application --bind 127.0.0.1:8080 --workers 3
