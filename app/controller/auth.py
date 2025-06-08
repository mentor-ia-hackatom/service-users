from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.user import Token, User, UserCreate
from app.models.user import User as UserModel
from app.utils.database import get_db
from app.core.security import verify_token
from app.services.user_service import UserService

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    session: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    print(form_data.username, form_data.password)
    return await UserService(session, request).authenticate_and_create_tokens(
        form_data.username,
        form_data.password
    )

@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    request: Request,
    refresh_token: str,
    session: Session = Depends(get_db)
) -> Any:
    return await UserService(session, request).refresh_user_tokens(refresh_token)

@router.post("/logout")
async def logout() -> Any:
    return {"message": "Successful logout"}

@router.get("/me", response_model=User)
async def read_users_me(
    request: Request,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_db)
) -> Any:
    return await UserService(session, request).get_current_user(token)

@router.post("/reset-password")
async def reset_password(
    email: str,
    request: Request,
    session: Session = Depends(get_db)
) -> Any:
    return await UserService(session, request).initiate_password_reset(email)
    
@router.post("/register")
async def register(
    request: Request,
    user: UserCreate,
    session: Session = Depends(get_db)
) -> Any:
    return UserService(session, request).create_user(user)