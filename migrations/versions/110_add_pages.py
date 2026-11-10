"""Добавить необязательное поле для числа страниц."""

from alembic import op
import sqlalchemy as sa


revision = "110"
down_revision = "100"


def upgrade() -> None:
    with op.batch_alter_table("books", table_kwargs={"sqlite_autoincrement": True}) as table:
        table.add_column(sa.Column("pages", sa.Integer, nullable=True))
        table.create_check_constraint("ck_books_positive_pages", "pages > 0")


def downgrade() -> None:
    with op.batch_alter_table("books", table_kwargs={"sqlite_autoincrement": True}) as table:
        table.drop_constraint("ck_books_positive_pages", type_="check")
        table.drop_column("pages")
