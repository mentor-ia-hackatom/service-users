from sqlalchemy import Boolean, Column, String, BigInteger, UUID
from sqlalchemy.sql import func
from app.utils.database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    uuid = Column(UUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(BigInteger, server_default=func.extract('epoch', func.now()))
    updated_at = Column(BigInteger, onupdate=func.extract('epoch', func.now()))