"""Консольный каталог книг на SQLite."""

import argparse
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from library import add_book, database_path, delete_book, export_csv, initialize, select_books
from models import BookInput


def print_books(path: Path, author: str | None = None) -> None:
    rows = select_books(path, author)
    if not rows:
        print("Книги не найдены.")
    for book_id, title, writer, pages in rows:
        size = f"{pages} стр." if pages else "объём не указан"
        print(f"{book_id}. {title} — {writer}, {size}")


def demo() -> None:
    with TemporaryDirectory() as folder:
        path = Path(folder) / "demo.sqlite3"
        initialize(path)
        add_book(path, "Два капитана", "Вениамин Каверин", 640)
        example = add_book(path, "Маленький принц", "Антуан де Сент-Экзюпери", 96)
        print_books(path)
        print(f"Экспортировано строк: {export_csv(path, path.with_suffix('.csv'))}")
        delete_book(path, example)
        print("После удаления:")
        print_books(path)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, default=database_path(), help="путь к SQLite")
    commands = parser.add_subparsers(dest="operation")
    commands.add_parser("init", help="применить миграции")
    select = commands.add_parser("select", help="показать книги")
    select.add_argument("--author")
    add = commands.add_parser("add", help="добавить книгу для проверки")
    add.add_argument("title")
    add.add_argument("author")
    add.add_argument("--pages", type=int)
    delete = commands.add_parser("delete", help="удалить книгу по ID")
    delete.add_argument("id", type=int)
    export = commands.add_parser("export", help="создать CSV с книгами")
    export.add_argument("destination", type=Path)
    args = parser.parse_args()

    try:
        if args.operation is None:
            demo()
        elif args.operation == "init":
            initialize(args.db)
            print(f"База готова: {args.db}")
        elif not args.db.is_file():
            parser.error("Сначала выполните команду init.")
        elif args.operation == "select":
            print_books(args.db, args.author)
        elif args.operation == "add":
            book = BookInput(title=args.title, author=args.author, pages=args.pages)
            book_id = add_book(args.db, book.title, book.author, book.pages)
            print(f"Добавлена книга №{book_id}.")
        elif args.operation == "delete":
            if not delete_book(args.db, args.id):
                parser.error(f"Книга №{args.id} не найдена.")
            print(f"Книга №{args.id} удалена.")
        elif args.operation == "export":
            count = export_csv(args.db, args.destination)
            print(f"Экспортировано книг: {count}.")
    except (sqlite3.Error, SQLAlchemyError, OSError, ValidationError) as error:
        parser.exit(1, f"Ошибка: {error}\n")


if __name__ == "__main__":
    main()
