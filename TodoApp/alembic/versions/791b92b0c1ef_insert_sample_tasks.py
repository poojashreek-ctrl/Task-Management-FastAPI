"""insert sample tasks

Revision ID: 791b92b0c1ef
Revises: 16d51f1e9b7f
Create Date: 2026-09-24 13:45:02.355191

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from datetime import datetime, timedelta


# revision identifiers, used by Alembic.
revision: str = '791b92b0c1ef'
down_revision: Union[str, Sequence[str], None] = '16d51f1e9b7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    task_table = sa.table(
        "task",
        sa.column("title", sa.String),
        sa.column("description", sa.String),
        sa.column("status", sa.String),
        sa.column("priority", sa.String),
        sa.column("due_date", sa.DateTime),
        sa.column("owner_id", sa.Integer),
    )

    tasks = []

    for i in range(1, 51):
        tasks.append({
            "title": f"Task {i}",
            "description": f"Description for task {i}",
            "status": "todo",
            "priority": "medium",
            "due_date": datetime.now() + timedelta(days=i),
            "owner_id": 1,
        })

    op.bulk_insert(task_table, tasks)


def downgrade():
    op.execute(
        "DELETE FROM task WHERE title LIKE 'Task %'"
    )