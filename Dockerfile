# Base Python
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para Cairo, Django, PDF, imágenes, etc.
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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar Python deps
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código
COPY . /app/

# STATICFILES (solo si ya tienes configurado collectstatic)
# RUN python manage.py collectstatic --noinput

# Puerto interno expuesto por el contenedor
EXPOSE 8080

# Comando de arranque con Gunicorn
CMD ["gunicorn", "barrovivo.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
