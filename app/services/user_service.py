from datetime import timedelta
from typing import Any, Optional
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash, verify_token
from app.models.user import User as UserModel
from app.schemas.user import UserCreate, UserUpdate, User, Token, UserGetOrCreate
from datetime import datetime
from app.core.security import verify_token
import logging

logger = logging.getLogger('UserService')

class DBSessionMixin:
    def __init__(self, session: Session):
        self.session = session

class AppDataAccess(DBSessionMixin):
    pass

class AppService(DBSessionMixin):
    def __init__(self, session: Session, request: Request):
        super().__init__(session)
        self.request = request

class UserDataAccess(AppDataAccess):
    def get_user_by_id(self, user_uuid: str) -> Optional[UserModel]:
        item = self.session.query(UserModel)
        item = item.filter(UserModel.uuid == user_uuid)
        item = item.first()
        return item if item else None

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.session.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, user_data: UserCreate, user_uuid: str = None) -> UserModel:
        db_user = UserModel(
            email=user_data.email,
            hashed_password=get_password_hash(user_data.password),
            full_name=user_data.full_name,
            created_at=datetime.now().timestamp(),
        )
        if user_uuid:
            db_user.uuid = user_uuid
        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)
        return db_user

    def update_user(self, user_uuid: str, user_data: UserUpdate) -> Optional[UserModel]:
        user = self.get_user_by_id(user_uuid)
        if not user:
            return None

        update_data = user_data.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        for field, value in update_data.items():
            setattr(user, field, value)

        self.session.commit()
        self.session.refresh(user)
        return user

    def delete_user(self, user_uuid: str) -> bool:
        user = self.get_user_by_id(user_uuid)
        if not user:
            return False

        self.session.delete(user)
        self.session.commit()
        return True

class UserService(AppService):
    def __init__(self, session: Session, request: Request):
        super().__init__(session, request)
        self.data_access = UserDataAccess(session)

    async def authenticate_and_create_tokens(self, email: str, password: str) -> dict:
        try:
            user = self.data_access.get_user_by_email(email)
            if not user or not verify_password(password, user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Inactive user"
                )
            
            token = self.create_tokens(str(user.uuid))
            return Token(**token)
        except Exception as ex:
            logger.error(f'Error to authenticate and create tokens - {ex}')
            raise HTTPException(status_code=500, detail=str(ex))

    async def refresh_user_tokens(self, refresh_token: str) -> dict:
        try:
            payload = await verify_token(refresh_token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = self.data_access.get_user_by_id(payload.get("sub"))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
        
            token = self.create_tokens(str(user.uuid))
            return Token(**token)
        except Exception as ex:
            logger.error(f'Error to refresh user tokens - {ex}')
            raise HTTPException(status_code=500, detail=str(ex))

    async def initiate_password_reset(self, email: str) -> dict:
        try:
            user = self.data_access.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            password = get_password_hash('123456')
            user.hashed_password = password
            self.data_access.update_user(user.uuid, UserUpdate(
                password=password,
                email=user.email,
                full_name=user.full_name
            ))
            self.session.commit()
            # For now we just return a message
            return {"message": "If the email exists, a password reset link will be sent"}
        except Exception as ex:
            logger.error(f'Error to initiate password reset - {ex}')
            raise HTTPException(status_code=500, detail=str(ex))
        
    def create_tokens(self, user_uuid: str) -> dict:
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_uuid}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": user_uuid})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def get_current_user(self, token: str) -> Optional[UserModel]:
        try:
            payload = await verify_token(token)

            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            
            user = self.data_access.get_user_by_id(payload.get("sub"))

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
            )

            return User(
                uuid=str(user.uuid),
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
            )

        except Exception as ex:
            logger.error(f'Error to get user - {ex}')
            raise HTTPException(status_code=500, detail=str(ex))
        
        return self.data_access.get_user_by_id(user_uuid)

    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.data_access.get_user_by_email(email)

    def create_user(self, user_data: UserCreate) -> UserModel:
        try:
            item = self.data_access.create_user(user_data)

            if not item: 
                raise Exception("Error al crear el usuario")
            
            item = User(
                uuid=str(item.uuid),
                email=item.email,
                full_name=item.full_name,
                is_active=item.is_active,
                created_at=item.created_at,
            )

            return {
                "status": True,
                "message": "User created successfully",
                "data": item
            }
        except Exception as e:
            logger.error(f"Error al crear el usuario: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def update_user(self, user_uuid: str, user_data: UserUpdate) -> Optional[UserModel]:
        return self.data_access.update_user(user_uuid, user_data)

    def delete_user(self, user_uuid: str) -> bool:
        return self.data_access.delete_user(user_uuid) 
    
    def get_or_create_user(self, user_data: UserGetOrCreate) -> bool:
        try:
            item = self.data_access.get_user_by_id(user_data.uuid)
            if item:
                return True
            else:
                hashed_password = get_password_hash('123456')
                item = self.data_access.create_user(
                    UserCreate(
                        email=user_data.email,
                        full_name=user_data.full_name,
                        password=hashed_password
                    ), 
                    user_data.uuid
                )
                return True
        except Exception as e:
            logger.error(f"Error to get or create user: {e}")
            raise HTTPException(status_code=500, detail=str(e))