"""Создать каталог с названием и автором."""

from alembic import op
import sqlalchemy as sa


revision = "100"
down_revision = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("title", sa.String(150), nullable=False),
        sa.Column("author", sa.String(120), nullable=False),
        sqlite_autoincrement=True,
    )


def downgrade() -> None:
    op.drop_table("books")
