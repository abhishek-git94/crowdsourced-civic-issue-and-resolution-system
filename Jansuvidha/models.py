from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Text, DateTime, Float, func, ForeignKey


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, server_default="citizen")

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} email={self.email!r} role={self.role!r}>"


class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    file: Mapped[str | None] = mapped_column(String(200), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # 🔥 add this missing field
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ML fields
    is_duplicate_of: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)
    upvotes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
