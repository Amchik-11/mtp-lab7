"""Описание общей схемы для SQLAlchemy и Alembic."""

from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints
from sqlalchemy import CheckConstraint, String, URL, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"
    __table_args__ = (CheckConstraint("pages > 0", name="ck_books_positive_pages"), {"sqlite_autoincrement": True})

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    author: Mapped[str] = mapped_column(String(120))
    pages: Mapped[int | None]


class PagesInput(BaseModel):
    pages: Annotated[int, Field(gt=0, le=1_000_000)] | None = None


class BookInput(PagesInput):
    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
    author: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]


class BookView(BookInput):
    model_config = ConfigDict(from_attributes=True)
    id: int


def engine_for(path: Path):
    return create_engine(URL.create("sqlite+pysqlite", database=str(path.resolve())))
