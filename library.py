"""Параметризованные SQL-запросы для консольных заданий."""

from contextlib import closing
import csv
import os
from pathlib import Path
import sqlite3

from alembic import command
from alembic.config import Config


def database_path() -> Path:
    return Path(os.getenv("READING_DB", "library.sqlite3")).resolve()


def migration_config(path: Path) -> Config:
    config = Config(str(Path(__file__).with_name("alembic.ini")))
    config.attributes["database_file"] = path
    return config


def initialize(path: Path) -> None:
    command.upgrade(migration_config(path), "head")


def add_book(path: Path, title: str, author: str, pages: int | None) -> int:
    with closing(sqlite3.connect(path)) as db, db:
        row = db.execute("INSERT INTO books (title, author, pages) VALUES (?, ?, ?)", (title, author, pages))
        return row.lastrowid


def select_books(path: Path, author: str | None = None) -> list[tuple]:
    query = "SELECT id, title, author, pages FROM books"
    where = " WHERE author = ?" if author is not None else ""
    params = (author,) if author is not None else ()
    with closing(sqlite3.connect(path)) as db:
        return db.execute(query + where + " ORDER BY author, title, id", params).fetchall()


def delete_book(path: Path, book_id: int) -> bool:
    with closing(sqlite3.connect(path)) as db, db:
        return db.execute("DELETE FROM books WHERE id = ?", (book_id,)).rowcount == 1


def export_csv(path: Path, destination: Path) -> int:
    rows = select_books(path)
    with destination.open("x", encoding="utf-8-sig", newline="") as output:
        writer = csv.writer(output)
        writer.writerow(("id", "title", "author", "pages"))
        writer.writerows(rows)
    return len(rows)
