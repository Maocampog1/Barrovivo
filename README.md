
# BARROVIVO

Proyecto 1 – Arquitectura de Software.  


---

## 1) Clonar el repositorio

Abre una terminal y clona el proyecto en tu PC:  

```bash
git clone https://github.com/Maocampog1/Barrovivo.git
cd Barrovivo
````

---

## 2) Requisitos

* Python **3.10+** (recomendado **3.11**)
* Pip instalado

Verifica versión de Python y pip:

```bash
python --version
pip --version
```

---

## 3) Instalar dependencias

Instala directamente en tu sistema (puedes usar entorno virtual si prefieres):

```bash
pip install -r requirements.txt
```

Si falta Django o alguna librería:

```bash
pip install "Django>=5,<6" pillow weasyprint==61.2
```

---

## 4) Preparar carpetas

Asegúrate de que existan estas carpetas:

* `static/` → ya viene incluida en el repo.
* `multimedia/` → créala si no existe, y coloca dentro un archivo `logo.png`.

Ejemplo en Linux/Mac:

```bash
mkdir -p multimedia
cp ruta/a/tu/logo.png multimedia/logo.png
```

En Windows crea la carpeta manualmente.

---

## 5) Migraciones y superusuario

Ejecuta las migraciones:

```bash
python manage.py migrate
```

Crea el usuario administrador:

```bash
python manage.py createsuperuser
```

---

## 6) Ejecutar el servidor

Levanta el servidor de desarrollo:

```bash
python manage.py runserver
```

Abre en tu navegador:
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 7) Problemas comunes

* **No carga el logo** → revisa que exista `multimedia/logo.png`.
* **Imágenes de productos no se ven** → revisa permisos de lectura/escritura en la carpeta `multimedia/`.

---

