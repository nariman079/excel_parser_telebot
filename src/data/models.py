import enum

from sqlalchemy import Integer, Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from src.data.database import Base


class Types(enum.Enum):
    ADMIN = 'admin'
    CUSTOMER = 'customer'


class User(Base):
    """
    Модель учителя
    """
    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )
    telegram_id = Column(
        Integer,
        unique=True
    )
    username = Column(
        String,
        unique=True
    )
    phone_number = Column(
        String
    )
    is_admin = Column(
        Boolean,
        default=False
    )


