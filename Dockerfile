# Base Python
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBUG=False
ENV DJANGO_SETTINGS_MODULE=Barrovivo.settings
ENV ALLOWED_HOSTS="*"

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

# Copiar e instalar dependencias Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt && pip cache purge

# Copiar el código del proyecto
COPY . /app/



# Ejecutar collectstatic
RUN mkdir -p /app/staticfiles /app/multimedia

RUN python manage.py collectstatic --noinput

# Exponer puerto del servidor
EXPOSE 8080

# Ejecutar collectstatic en runtime y servir con runserver temporalmente
CMD ["gunicorn", "Barrovivo.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
