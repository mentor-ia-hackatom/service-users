
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.schemas.user import UserGetOrCreate
from app.utils.database import get_db
from app.core.security import verify_token
from app.services.user_service import UserService

router = APIRouter(prefix="/internal/users_services", tags=["Users Services"])


@router.patch("/get_or_create_user")
def get_or_create_user(
    user_data: UserGetOrCreate,
    request: Request,
    session: Session = Depends(get_db)
) -> Any:
    return UserService(session, request).get_or_create_user(user_data)