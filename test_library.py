"""Общая база для SQL, Alembic и REST API."""

from contextlib import closing
import csv
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from alembic import command
from fastapi.testclient import TestClient

from api import create_app
from library import add_book, delete_book, export_csv, initialize, migration_config, select_books


class LibraryTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.path = Path(folder.name) / "books.sqlite3"

    def test_migration_keeps_titles_and_author(self):
        config = migration_config(self.path)
        command.upgrade(config, "100")
        with closing(sqlite3.connect(self.path)) as db, db:
            db.execute("INSERT INTO books (title, author) VALUES (?, ?)", ("Повесть", "Автор"))
        initialize(self.path)
        self.assertEqual(select_books(self.path), [(1, "Повесть", "Автор", None)])
        command.downgrade(config, "100")
        with closing(sqlite3.connect(self.path)) as db:
            self.assertEqual(db.execute("SELECT title, author FROM books").fetchone(), ("Повесть", "Автор"))
        initialize(self.path)
        command.check(config)

    def test_sql_and_api_see_same_catalog(self):
        initialize(self.path)
        book_id = add_book(self.path, "Два капитана", "Каверин", None)
        with TestClient(create_app(self.path)) as client:
            self.assertEqual(client.get("/books", params={"author": "Каверин"}).json()[0]["id"], book_id)
            endpoint = f"/books/{book_id}"
            self.assertEqual(client.patch(f"{endpoint}/pages", json={"pages": -1}).status_code, 422)
            self.assertEqual(client.patch(f"{endpoint}/pages", json={"pages": 640}).status_code, 200)
            created = client.post("/books", json={"title": "Маленький принц", "author": "Экзюпери"})
            self.assertEqual(created.status_code, 201)
            csv_path = self.path.with_suffix(".csv")
            self.assertEqual(export_csv(self.path, csv_path), 2)
            with csv_path.open(encoding="utf-8-sig", newline="") as source:
                self.assertEqual({row["title"]: row["pages"] for row in csv.DictReader(source)},
                                 {"Два капитана": "640", "Маленький принц": ""})
            self.assertTrue(delete_book(self.path, book_id))
            self.assertEqual(client.get(endpoint).status_code, 404)
            self.assertEqual(client.delete(f"/books/{created.json()['id']}").status_code, 204)
            self.assertEqual(select_books(self.path), [])
