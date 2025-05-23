# Prueba Técnica Backend - API REST

Esta es una API REST desarrollada como prueba técnica. La aplicación proporciona endpoints para gestionar usuarios, autenticación y procesamiento de imágenes con diferentes filtros y transformaciones.

## Tecnologías Utilizadas

- **FastAPI 0.104.1** - Framework web moderno y rápido para APIs
- **MongoDB** - Base de datos NoSQL
- **MongoEngine 0.27.0** - ODM para MongoDB
- **PyMongo 4.6.1** - Driver oficial de MongoDB para Python
- **Pydantic 2.4.2** - Validación de datos y configuración
- **Uvicorn 0.24.0** - Servidor ASGI
- **Python-dotenv 1.0.0** - Manejo de variables de entorno
- **Passlib 1.7.4** - Hash de contraseñas con bcrypt
- **Python-jose 3.3.0** - Manejo de JWT
- **Pillow 10.1.0** - Procesamiento de imágenes
- **Docker** - Contenedorización de la aplicación

## Prerrequisitos

- Python 3.11 o superior
- MongoDB
- Docker y Docker Compose
- Git

## Instalación y Ejecución

### Usando Docker

1. Clona el repositorio:
```bash
git clone https://github.com/DaveOval/prueba-tecnica-back
cd prueba-tecnica-back
```

2. Configura las variables de entorno:
Crea un archivo `.env` en la raíz del proyecto (Existe un template `.env.template`):
```
MONGO_URI='mongodb://admin:admin123@localhost:27017/'
SECRET_KEY='KFC'
FRONTEND_URL='http://localhost:3000'
```

3. Construye y ejecuta los contenedores:
```bash
# Construir las imágenes
docker-compose build

# Iniciar los contenedores en modo detached
docker-compose up -d

```

4. Para detener los contenedores:
```bash
docker-compose down
```

La API estará disponible en `http://localhost:8000`

### Desarrollo Local (Sin Docker)

1. Crea y activa un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Configura las variables de entorno:
Crea un archivo `.env` en la raíz del proyecto (Existe un template `.env.template`):
```
MONGO_URI='mongodb://admin:admin123@localhost:27017/'
SECRET_KEY='KFC'
FRONTEND_URL='http://localhost:3000'
```

4. Ejecuta el servidor de desarrollo:
```bash
uvicorn app.main:app --reload
```

## Características Principales

### Procesamiento de Imágenes
- Subida de imágenes con validación de formato y tamaño
- Procesamiento de imágenes con múltiples filtros:
  - Escala de grises (grayscale)
  - Desenfoque (blur)
  - Miniatura (thumbnail)
  - Efecto sepia
  - Inversión de colores
  - Ajuste de brillo
- Almacenamiento de imágenes originales y procesadas
- Gestión de imágenes por usuario
- Endpoints para:
  - Subir imágenes
  - Procesar imágenes con diferentes filtros
  - Obtener imágenes originales y procesadas
  - Servir imágenes en formato base64

### Seguridad y Autenticación
- Autenticación con JWT
- Hash seguro de contraseñas con bcrypt
- Validación de datos con Pydantic
- Manejo de errores y excepciones
- CORS configurado para desarrollo
- Validación de propiedad de imágenes