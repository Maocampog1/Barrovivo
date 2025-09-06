
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
¡Perfecto! Aquí tienes un bloque listo para pegar en tu README explicando **cuándo** usar los comandos de traducción y **qué instalar** (solo si vas a editar traducciones).

---

## 8) i18n / Traducciones 

Django usa catálogos **gettext** en `locale/`:

```
locale/
  es/LC_MESSAGES/django.po  # texto
  es/LC_MESSAGES/django.mo  # binario compilado
  en/LC_MESSAGES/django.po
  en/LC_MESSAGES/django.mo
```

### Si **NO vas a modificar** textos traducibles

No necesitas instalar nada extra.
Simplemente corre:

```bash
python manage.py runserver
```

> Esto se puede hacer ya que los  **.mo** estan en el repo.

###  **SÍ vas a modificar** o agregar traducciones

Necesitarás las herramientas **GNU gettext** para ejecutar estos comandos:

1. **Extraer** cadenas nuevas/actualizadas hacia los `.po`:

```bash
python manage.py makemessages -l es -l en
```

2. Edita los `.po` (rellena `msgstr ""` con la traducción).

3. **Compilar** a `.mo`:

```bash
python manage.py compilemessages
```

#### Windows 

* Instala **Poedit** (trae gettext)
* Asegúrate de tener estas rutas en tu PATH (temporal o permanentemente):

  * `C:\Program Files (x86)\Poedit\GettextTools\bin`
  * (si falta `msgattrib`) también: `C:\Program Files\gettext-iconv\bin`
* Verifica:

```powershell
where msguniq
where xgettext
where msgfmt
where msgattrib
```

#### Tips

* Si `compilemessages` marca **duplicados** en un `.po`:

  ```powershell
  msguniq --use-first -o django.po django.po
  python manage.py compilemessages
  ```
* Cada vez que cambies textos con `{% trans %}` (templates) o `_('...')` (Python),
  repite: **makemessages → editar .po → compilemessages**.

> Nota: Solo se traducen textos **marcados** con `{% trans %}` / `{% blocktrans %}` o `_("...")`.
> Agregar entradas “a mano” en el `.po` sin marcar los textos en código no surtirá efecto.

---


