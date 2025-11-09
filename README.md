# 📚 Sistema de Biblioteca Digital

Este es un proyecto web completo desarrollado con Django que simula un sistema de gestión de una biblioteca digital. Permite la administración de libros, autores y categorías, así como un sistema de préstamos y reservas por parte de los usuarios.

El proyecto cumple con los requisitos de un sistema MVT (Modelo-Vista-Template), incluyendo autenticación de usuarios con roles, operaciones CRUD completas y un panel de administración con reportes.

---

## 🚀 Características Implementadas

### Requisitos Funcionales
* **Autenticación y Roles:** Sistema de registro, inicio de sesión y cierre de sesión. El sistema distingue entre dos roles:
    * **Lector:** Puede ver el catálogo y gestionar sus propios préstamos.
    * **Bibliotecario:** Puede gestionar el catálogo (CRUD de libros) y todos los préstamos.
* **Gestión de Catálogo (CRUD):** Los bibliotecarios pueden crear, leer, actualizar y eliminar Libros, Autores y Categorías.
* **Sistema de Préstamos:**
    * Los lectores pueden pedir prestados libros disponibles (por 14 días).
    * Los bibliotecarios pueden ver todos los préstamos y marcarlos como "devueltos".
    * Los lectores pueden ver su historial de préstamos y el estado (en curso, devuelto, retrasado).
* **Control de Estado:** Los libros se marcan automáticamente como "Prestado" o "Disponible".
* **Sanciones (Control de Retrasos):** El sistema detecta y muestra visualmente los préstamos que han superado su fecha de devolución.

### Panel de Administración (Dashboard)
* **Estadísticas:** Tarjetas con KPIs (Total de Libros, Total de Lectores, Préstamos Activos).
* **Gráficos Dinámicos (Chart.js):**
    * Un gráfico de barras que muestra el total de préstamos por mes.
    * Un gráfico de dona que muestra el "Top 5" de libros más prestados.

### Reportes y Notificaciones
* **Exportación de Reportes:**
    * Descarga de un reporte de **Excel** (`.xlsx`) con la lista completa de libros (usando `pandas`).
    * Descarga de un reporte **PDF** (`.pdf`) con la lista de préstamos activos (usando `reportlab`).
* **Notificaciones por Correo (simulado en consola):**
    * Envío de correo de **confirmación** al lector cuando pide un libro.
    * Comando de gestión (`enviar_recordatorios`) para notificar a usuarios sobre **vencimientos** próximos.

---

## 🛠️ Stack de Tecnologías

* **Backend:** Python 3, Django
* **Base de Datos:** SQLite3 (por defecto en desarrollo)
* **Frontend:** HTML5, CSS3, Bootstrap 5
* **Reportes:**
    * `pandas` y `openpyxl` (para Excel)
    * `reportlab` (para PDF)
* **Gráficos:** `Chart.js`

---

## 💻 Instalación y Ejecución Local

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### 1. Prerrequisitos
* Tener Python 3.x instalado.
* Tener `pip` (el gestor de paquetes de Python) instalado.

### 2. Clonar y Configurar el Entorno

```bash
# 1. Clona este repositorio (o descarga el ZIP)
# git clone https://...

# 2. Navega a la carpeta raíz del proyecto
cd biblioteca_proyecto

# 3. Crea un entorno virtual
python -m venv venv

# 4. Activa el entorno virtual
# En Windows:
# venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate


# 1. Instala Django y las bibliotecas de reportes
pip install django pandas openpyxl reportlab

# 2. (Opcional) Si tienes un archivo requirements.txt:
# pip install -r requirements.txt



# 1. Inicia el servidor de desarrollo
python manage.py runserver

# 2. Abre tu navegador y ve a: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)



python manage.py enviar_recordatorios