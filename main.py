from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.controller.auth import router as auth_router
from app.controller.users_controller import router as users_router
from app.utils.database import get_db
from app.core.security import verify_token
from fastapi.responses import JSONResponse
from fastapi import Request, HTTPException, status

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    redoc_url=None  # Deshabilitamos redoc por defecto
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers
app.include_router(auth_router)
app.include_router(users_router)


EXCLUDED_PATHS = ["/api/v1/auth/login", "/api/v1/auth/refresh_token", "/api/v1/auth/register", "/api/v1/auth/reset-password", "/docs", "/redoc", "/openapi.json"]

@app.middleware("http")
async def access_token_middleware(request: Request, call_next):
    # Allow OPTIONS requests without authentication
    if request.method == "OPTIONS":
        return await call_next(request)
    # Skip token check for internal API
    if request.headers.get("X-HTTP-PURPOSE") == "internal":
        return await call_next(request)
    
    # Skip token check for excluded paths
    if request.url.path in EXCLUDED_PATHS or (request.url.path == "/auth" and request.method == "POST"):
        return await call_next(request)
    
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Missing or invalid access token"},
        )
    access_token = auth_header.split(" ")[1]

    try:
        user = verify_token(access_token)
        request.state.user = user
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"detail": e.detail})
    return await call_next(request)
