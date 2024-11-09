from sqlalchemy import Integer, Column, String, Boolean, BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from src.config import Base


class User(Base):
    """
    Модель учителя
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = Column(BigInteger, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)

