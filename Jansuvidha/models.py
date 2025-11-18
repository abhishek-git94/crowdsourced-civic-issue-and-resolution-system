from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Text, DateTime, Float, func


class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # In your app.py you use `name` and `password` fields — keep those names to be compatible.
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    # store password hash in the `password` column (string). If you prefer `password_hash`,
    # we can add a compatibility alias later — kept `password` to match existing code.
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, server_default="citizen")

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} email={self.email!r} role={self.role!r}>"

class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # reporter name (string)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # textual issue description (AI-generated or user-provided)
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    # human-friendly location string
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    # saved file path relative to `static/`, e.g. "uploads/abc.jpg"
    file: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="Pending")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Issue id={self.id} name={self.name!r} status={self.status!r}>"