"""REST API книжного каталога на FastAPI и SQLAlchemy."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from library import database_path
from models import Book, BookInput, BookView, PagesInput, engine_for


def create_app(path: Path | None = None) -> FastAPI:
    engine = engine_for(path or database_path())

    @asynccontextmanager
    async def lifespan(_app):
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Книжный каталог · ЛР №7", lifespan=lifespan)

    def session():
        with Session(engine) as db:
            yield db

    def require_book(db: Session, book_id: int) -> Book:
        book = db.get(Book, book_id)
        if book is None:
            raise HTTPException(status_code=404, detail="Книга не найдена")
        return book

    @app.get("/books", response_model=list[BookView])
    def books(author: str | None = None, db: Session = Depends(session)):
        query = select(Book).order_by(Book.author, Book.title, Book.id)
        if author is not None:
            query = query.where(Book.author == author)
        return db.scalars(query).all()

    @app.get("/books/{book_id}", response_model=BookView)
    def get_book(book_id: int, db: Session = Depends(session)):
        return require_book(db, book_id)

    @app.post("/books", response_model=BookView, status_code=201)
    def create_book(book: BookInput, db: Session = Depends(session)):
        record = Book(**book.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @app.patch("/books/{book_id}/pages", response_model=BookView)
    def set_pages(book_id: int, value: PagesInput, db: Session = Depends(session)):
        record = require_book(db, book_id)
        record.pages = value.pages
        db.commit()
        db.refresh(record)
        return record

    @app.delete("/books/{book_id}", status_code=204)
    def remove_book(book_id: int, db: Session = Depends(session)):
        db.delete(require_book(db, book_id))
        db.commit()
        return Response(status_code=204)

    return app


app = create_app()
