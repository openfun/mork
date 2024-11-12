"""Add timestamp fields to email tables

Revision ID: 976e462b45b6
Revises: 608d075c6e99
Create Date: 2024-11-05 16:27:23.065141

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "976e462b45b6"
down_revision: Union[str, None] = "608d075c6e99"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "email_status",
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
    )
    op.add_column(
        "email_status", sa.Column("updated_at", sa.DateTime(), nullable=False)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("email_status", "updated_at")
    op.drop_column("email_status", "created_at")
    # ### end Alembic commands ###