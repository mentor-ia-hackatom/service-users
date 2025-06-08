# Microservicio de Gestión de Usuarios

Este microservicio proporciona una API RESTful para la gestión de usuarios, incluyendo autenticación, registro y gestión de perfiles de usuario. Está construido con FastAPI y utiliza Supabase como base de datos.

## Características Principales

- Autenticación de usuarios (login, registro, refresh token)
- Gestión de perfiles de usuario
- API RESTful con documentación Swagger
- Integración con Supabase
- Middleware de autenticación con JWT
- CORS configurado para desarrollo

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Cuenta en Supabase (para la base de datos)

## Configuración del Entorno Local

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd service-users
```

2. Crear un entorno virtual e instalar dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurar variables de entorno:
   - Copiar el archivo `.env.example` a `.env`
   - Completar las variables de entorno necesarias:
     - `DATABASE_URL`: URL de conexión a Supabase
     - `SECRET_KEY`: Clave secreta para JWT
     - `ALGORITHM`: Algoritmo para JWT (por defecto: HS256)
     - `ACCESS_TOKEN_EXPIRE_MINUTES`: Tiempo de expiración del token
     - `PROJECT_NAME`: Nombre del proyecto
     - `VERSION`: Versión del proyecto

4. Ejecutar el servidor de desarrollo:
```bash
uvicorn main:app --reload
```

El servidor estará disponible en `http://localhost:4000`

## Documentación de la API

Una vez que el servidor esté en ejecución, puedes acceder a:
- Documentación Swagger UI: `http://localhost:4000/docs`
- Especificación OpenAPI: `http://localhost:4000/openapi.json`

## Endpoints Principales

- `/api/v1/auth/login`: Autenticación de usuarios
- `/api/v1/auth/register`: Registro de nuevos usuarios
- `/api/v1/auth/refresh_token`: Renovación de tokens
- `/api/v1/auth/reset-password`: Restablecimiento de contraseña
- `/api/v1/users`: Gestión de usuarios

## Estructura del Proyecto

```
service-users/
├── app/
│   ├── core/
│   ├── controller/
│   └── utils/
├── main.py
├── requirements.txt
└── .env
```

## Desarrollo

Para contribuir al proyecto:

1. Crear una nueva rama para tus cambios
2. Implementar las modificaciones
3. Ejecutar las pruebas
4. Crear un pull request

## Licencia

© 2025 Lucio Gabriel Abaca. Todos los derechos reservados. 