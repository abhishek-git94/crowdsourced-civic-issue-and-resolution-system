from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy import (
    Integer, String, Text, DateTime, Float, ForeignKey,
    UniqueConstraint, func
)
from flask_login import UserMixin


# ------------------------------------------
# Base class
# ------------------------------------------
class Base(DeclarativeBase):
    pass


# ==========================================
# USER MODEL
# ==========================================
class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, server_default="citizen")

    # relationships
    issues: Mapped[list["Issue"]] = relationship(back_populates="user")
    upvotes: Mapped[list["Upvote"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User id={self.id} name={self.name!r} email={self.email!r}>"


# ==========================================
# ISSUE MODEL
# ==========================================
class Issue(Base):
    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    issue: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[str] = mapped_column(String(200), nullable=False)
    file: Mapped[str | None] = mapped_column(String(200), nullable=True)

    status: Mapped[str] = mapped_column(String(50), nullable=False, default="Pending")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    severity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # ML duplicate detection
    is_duplicate_of: Mapped[int | None] = mapped_column(Integer, nullable=True)
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Upvote count
    upvotes: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # relationships
    user: Mapped["User"] = relationship(back_populates="issues")
    upvote_records: Mapped[list["Upvote"]] = relationship(back_populates="issue")

    def __repr__(self):
        return f"<Issue id={self.id} issue={self.issue[:20]!r}>"


# ==========================================
# UPVOTE MODEL
# ==========================================
class Upvote(Base):
    __tablename__ = "upvotes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    issue_id: Mapped[int] = mapped_column(ForeignKey("issues.id"), nullable=False)

    # ensure one upvote per user per issue
    __table_args__ = (UniqueConstraint("user_id", "issue_id", name="uq_user_issue"),)

    # relationships
    user: Mapped["User"] = relationship(back_populates="upvotes")
    issue: Mapped["Issue"] = relationship(back_populates="upvote_records")

    def __repr__(self):
        return f"<Upvote user={self.user_id} issue={self.issue_id}>"
