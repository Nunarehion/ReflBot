from sqlalchemy import BigInteger, VARCHAR, TIMESTAMP, func, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    full_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), default=func.now())
    is_premium: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

class Message(Base):
    __tablename__ = "messages"
    
    message_id: Mapped[str] = mapped_column(VARCHAR(255), primary_key=True)
    text: Mapped[str] = mapped_column(nullable=False)