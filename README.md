# BARROVIVO 

Proyecto 1 Arquitectura de Software.

## 1) Requisitos

* Python 3.10+ (recomendado 3.11)
* Pip instalado

## 2) Instalar dependencias

Instala directamente en tu sistema (sin entorno virtual):

```bash
pip install -r requirements.txt
```

Si falta Django:

```bash
pip install "Django>=5,<6" pillow weasyprint==61.2
```

## 3) Preparar carpetas

Asegúrate de tener:

* `static/` (ya existe)
* `multimedia/` (créala si no está) con `logo.png` adentro.

## 4) Migraciones y superusuario

```bash
python manage.py migrate
python manage.py createsuperuser
```

## 5) Ejecutar servidor

```bash
python manage.py runserver
```

Entra a: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## 6 Problemas comunes

* No carga logo → revisa `multimedia/logo.png`.
* Error con WeasyPrint → instala dependencias del sistema o usa impresión desde navegador.
* Imágenes de productos no se ven → revisa permisos en `multimedia/`.

