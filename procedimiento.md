# Procedimiento de Desarrollo - Fase 0: Git y Repositorio

Antes de comenzar con Docker, es fundamental tener el proyecto bajo control de versiones y vinculado a GitHub.

### Paso 0: Inicializar Git y vincular GitHub

1. Asegúrate de estar en la carpeta raíz del proyecto: `/home/mauri/uni/UTN/prograIIAyacucho/menus`
2. Ejecuta los siguientes comandos en tu terminal:

```bash
# 1. Inicializar el repositorio local
git init

# 2. Vincular con tu repositorio remoto en GitHub
git remote add origin https://github.com/fiemcasals/softAyacucho.git

# 3. Crear un archivo .gitignore básico para no subir basura
cat <<EOF > .gitignore
__pycache__/
*.py[cod]
*$py.class
.env
db.sqlite3
/media/
/static/
EOF

#si no les funciona usen la IGU

# 4. Primer commit
git add .
git commit -m "Inicio de proyecto modular - Estructura Base y CV"

# 5. Asegurar branch principal e inicializar la subida
git branch -M main #es peligroso renombrar ramas si trabajo en equipo.
#por defecto github crea en las versiones viejas a master como rama principal.
git push -u origin main
```

---

# Procedimiento de Desarrollo - Fase 1: Entorno de Docker y Proyecto Base

> **📂 ESTRUCTURA DEL PROYECTO PARA NO CONFUNDIRSE:**
> - `/menus/` -> Tu carpeta principal (Raíz donde está el `docker-compose.yml`)
> - `/menus/config/` -> Carpeta con la configuración central (`settings.py`, `urls.py`)
> - `/menus/login/` -> App donde está tu CV
> - `/menus/recetas/` -> App de Recetas

### Paso 1: Crear los archivos base del entorno 

> **🚨 MUY IMPORTANTE:** Asegúrate de estar posicionado en **`/home/mauri/uni/UTN/prograIIAyacucho/menus`** en tu terminal. 

1. Abre tu terminal y asegúrate de estar en el directorio del proyecto: `/home/mauri/uni/UTN/prograIIAyacucho/menus` (puedes verificarlo con el comando **`pwd`** en Linux/Mac o **`cd`** en Windows).
2. Crea allí (dentro de `menus/`) un archivo llamado **`requirements.txt`** y pega el siguiente código:
```text
Django>=5.0,<5.1
psycopg2-binary>=2.9
Pillow>=10.0
```
*(Nota: Pillow es necesario para las imágenes de las recetas, psycopg2 para administrar la BD).*

3. Crea un archivo llamado **`Dockerfile`** y pega las siguientes instrucciones:
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/
```

4. Crea un archivo llamado **`docker-compose.yml`** y pega las directivas de los dos contenedores:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=menus_db
      - POSTGRES_USER=menus_user
      - POSTGRES_PASSWORD=menus_pass
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
```

5. Crea un archivo oculto llamado **`.env`** donde mapeamos configuraciones sensibles para Django y Docker:
```env
DEBUG=1
SECRET_KEY=clave_secreta_provisional_para_desarrollo
DB_NAME=menus_db
DB_USER=menus_user
DB_PASSWORD=menus_pass
DB_HOST=db
DB_PORT=5432
```

### Paso 1.5: Corregir Permisos (Linux)
Como Docker crea los archivos como usuario "root", es posible que no puedas editarlos. Corré esto en tu terminal para que los archivos te pertenezcan a vos:
```bash
sudo chown -R $USER:$USER .
```

### Paso 2: Generar y enlazar el Proyecto y sus Apps 
En la misma terminal, usa los siguientes comandos para crear la estructura de Django "dentro" del contenedor.

1. Iniciar el proyecto core (El punto `.` del final es obligatorio para no anidar carpetas):
```bash
docker compose run --rm web django-admin startproject menus .
```

2. Crear la app de "login":
```bash
docker compose run --rm web python manage.py startapp login
```

3. Crear la app de "recetas":
```bash
docker compose run --rm web python manage.py startapp recetas
```

> **💡 TIP DE PERMISOS:** Cada vez que Docker crea una carpeta nueva (como al hacer `startapp`), la crea como usuario "root". Repetí el comando del paso 1.5 (`sudo chown -R $USER:$USER .`) para volver a tomar posesión de las carpetas nuevas.

### Paso 3: Correr y Verificar el entorno temporalmente 
1. Levanta todos los servicios en segundo plano:
```bash
docker compose up -d
```
2. Anda a tu navegador e ingresa a `http://localhost:8000`. Deberías ver la famosa página del cohete ("The install worked successfully!").

---

### Fase 2: Configuración de Settings y Registro de Apps

1. Abrí **`menus/config/settings.py`** y agregá tus dos apps (`login` y `recetas`) a la lista de `INSTALLED_APPS`:
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Nuestras apps
    'login',
    'recetas',
]
```

2. Agregá esto **al final** de **`menus/config/settings.py`**:
```python
import os

STATIC_URL = 'static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

### Fase 3: Creación de la Vista, el Template (CV) y Rutas (URLs)
Vamos a crear tu propia página de Currículum (CV) dentro de la app `login`.

1. **Crear la carpeta para el HTML:**
   Adentro de la carpeta de login: **`menus/login/templates/login/`**.
   
2. **Crear el archivo HTML del CV:**
   Crea el archivo en: **`menus/login/templates/login/cv.html`**.

```html
<!-- CV BALANCEADO - MAURICIO CASALS -->
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Profesional - Mauricio Casals</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #1a365d; --secondary: #2b6cb0; --accent: #4299e1; --text-dark: #2d3748; --text-light: #718096; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background-color: #e2e8f0; line-height: 1.6; padding: 40px 20px; }
        .cv-wrapper { max-width: 1050px; margin: 0 auto; background: white; display: flex; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); border-radius: 8px; overflow: hidden; }
        .sidebar { width: 35%; background-color: var(--primary); color: white; padding: 40px 25px; }
        .photo-container { text-align: center; margin-bottom: 30px; }
        .photo-container img { width: 200px; height: 200px; border-radius: 50%; border: 5px solid var(--accent); object-fit: cover; object-position: top; }
        .sidebar-section { margin-bottom: 30px; }
        .sidebar-title { font-size: 1.1rem; font-weight: 700; text-transform: uppercase; border-bottom: 2px solid var(--accent); padding-bottom: 8px; margin-bottom: 12px; }
        .sidebar-item { margin-bottom: 15px; font-size: 0.85rem; }
        .sidebar-item strong { display: block; color: var(--accent); font-size: 0.95rem; }
        .main-content { width: 65%; padding: 40px 45px; }
        .header { margin-bottom: 25px; }
        .header h1 { font-size: 2.5rem; color: var(--primary); text-transform: uppercase; }
        .header h2 { font-size: 1.1rem; color: var(--secondary); font-weight: 500; margin-bottom: 15px; }
        .contact-horizontal { display: flex; gap: 20px; font-size: 0.9rem; color: var(--text-light); margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid #edf2f7; }
        .section { margin-bottom: 35px; }
        .section-title { font-size: 1.3rem; color: var(--primary); font-weight: 700; border-left: 5px solid var(--secondary); padding-left: 15px; }
        .entry { margin-bottom: 25px; }
        .entry-title { font-weight: 700; color: #1a202c; font-size: 1.05rem; }
        .entry-date { color: var(--accent); font-weight: 600; font-size: 0.85rem; }
        .entry-company { color: var(--secondary); font-weight: 600; font-size: 0.95rem; }
        .entry-desc { font-size: 0.9rem; color: var(--text-dark); margin-top: 5px; }
        .skills-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .skill-tag { background: #edf2f7; padding: 4px 10px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; color: var(--primary); text-align: center; }
        @media (max-width: 768px) { .cv-wrapper { flex-direction: column; } .sidebar, .main-content { width: 100%; } .contact-horizontal { flex-direction: column; gap: 5px; } }
    </style>
</head>
<body>
<div class="cv-wrapper">
    <aside class="sidebar">
        <div class="photo-container"><img src="/media/perfil.png" alt="Mauri"></div>
        <div class="sidebar-section">
            <h3 class="sidebar-title">Educación</h3>
            <div class="sidebar-item"><strong>Ingeniería</strong>FIE | 2021-2025</div>
            <div class="sidebar-item"><strong>Licenciatura</strong>2009-2012</div>
        </div>
        <div class="sidebar-section">
            <h3 class="sidebar-title">Habilidades</h3>
            <div class="skills-grid">
                <span class="skill-tag">Python</span><span class="skill-tag">Java</span>
                <span class="skill-tag">JS</span><span class="skill-tag">C/C++</span>
            </div>
        </div>
    </aside>
    <main class="main-content">
        <header class="header">
            <h1>MAURICIO CASALS</h1>
            <h2>Ingeniero Informático & Licenciado en Gestión</h2>
            <div class="contact-horizontal">
                <span><strong>Email:</strong> mauriciocasals90@gmail.com</span>
                <span><strong>Ubicación:</strong> CABA, Buenos Aires</span>
            </div>
        </header>
        <section class="section">
            <h3 class="section-title">Experiencia Profesional</h3>
            <div class="entry">
                <div class="entry-header"><span class="entry-title">Coordinador y Profesor Univ.</span><span class="entry-date">ACTUAL</span></div>
                <div class="entry-company">UTN</div>
            </div>
            <div class="entry">
                <div class="entry-header"><span class="entry-title">Líder y Evaluador</span><span class="entry-date">ACTUAL</span></div>
                <div class="entry-company">Ejército Argentino</div>
            </div>
        </section>
    </main>
</div>
</body>
</html>
```

3. **Crear la vista en Python que muestra el HTML:**
   Abrí el archivo `menus/login/views.py` y dejalo así:
```python
from django.shortcuts import render

def vista_cv(request):
    return render(request, 'login/cv.html')
```

4. **Configurar las URLs de la app `login`:**
   Creá un archivo nuevo llamado `urls.py` directamente dentro de la carpeta `login` (`menus/login/urls.py`) y escribí esto:
```python
from django.urls import path
from . import views

urlpatterns = [
    path('cv/', views.vista_cv, name='cv'),
]
```

5. **Enganchar las URLs de `login` a las URLs de la configuración central:**
   Abrí el archivo central de rutas: **`menus/config/urls.py`** y modificalo para incluir y detectar nuestra nueva app:
```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Conectamos nuestras URLs de login al proyecto general
    path('login/', include('login.urls')), 
]
```

### Paso 4: ¡Ver tu CV en el Buscador!
1. **Correr el contenedor:** Si no anda en automatico puedes reiniciar todo con este comando:
```bash
docker compose up -d
```
2. **Entender la URL:** La dirección es **`/login/cv/`** porque se suma la ruta de la app (`login/`) más la ruta de la vista (`cv/`).
3. **Ver el resultado:** Andá a tu navegador e ingresá: http://localhost:8000/login/cv/

---

### Fase 4: Integración de Foto y Archivos Media (Imágenes)
Para que el CV muestre tu foto real en lugar de un círculo genérico, seguí estos pasos:

1. **Crear la carpeta de medios (Si no existe):**
   Corré este comando en tu terminal parado en la raíz `/menus/`:
```bash
mkdir -p media
```
*(Y recordá que si te da error de permisos, debés correr `sudo chown -R $USER:$USER .` de nuevo).*

2. **Cargar y Renombrar tu foto:**
   Tenés que poner tu foto dentro de esa carpeta `/media/` y el archivo debe llamarse exactamente **`perfil.png`**.
   
   > [!IMPORTANT]
   > Asegurate de que la extensión sea **`.png`**. Si tu archivo termina en `.jpeg` o `.jpg`, debés renombrarlo a `.png`, de lo contrario Django no lo encontrará y verás una imagen rota.

3. **Configuración Técnica realizada:**
   Para que esto funcione, yo ya modifiqué los siguientes archivos por vos:
   - **`config/settings.py`**: Se agregaron las rutas de `MEDIA_URL` y `MEDIA_ROOT`.
   - **`config/urls.py`**: Se añadió la lógica de `static(settings.MEDIA_URL, ...)` para que el navegador pueda "ver" los archivos de la carpeta media.
   - **`login/templates/login/cv.html`**: Se actualizó el `<img>` para que use `/media/perfil.png`.

4. **Resultado:**
   Una vez que la foto esté en su lugar con el nombre correcto, simplemente refrescá:
   [http://localhost:8000/login/cv/](http://localhost:8000/login/cv/)

¡Avisame cuando puedas ver tu nuevo y moderno CV andando! Con esto habremos dominado las URLs y Templates en formato modular.
