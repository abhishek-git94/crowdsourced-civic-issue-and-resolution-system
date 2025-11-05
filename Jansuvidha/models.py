from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, func

class Base(DeclarativeBase):
    pass

class Issue(Base):
    __tablename__ = "issues"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    file: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())