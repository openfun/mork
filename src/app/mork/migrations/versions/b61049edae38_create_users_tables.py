"""Create users tables

Revision ID: b61049edae38
Revises: 976e462b45b6
Create Date: 2024-11-08 10:38:01.575241

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b61049edae38"
down_revision: Union[str, None] = "976e462b45b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=254), nullable=False),
        sa.Column("edx_user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column(
            "reason",
            sa.Enum("USER_REQUESTED", "GDPR", name="deletion_reason"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("edx_user_id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "user_service_statuses",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "service_name",
            sa.Enum("ASHLEY", "EDX", "BREVO", "JOANIE", name="service_name"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("TO_DELETE", "DELETING", "DELETED", name="deletion_status"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "service_name", name="uq_record_service"),
    )
    op.create_index(
        "idx_service_status",
        "user_service_statuses",
        ["service_name", "status"],
        unique=False,
    )
    op.create_index(
        "idx_user_service_status",
        "user_service_statuses",
        ["user_id", "service_name", "status"],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_user_service_status", table_name="user_service_statuses")
    op.drop_index("idx_service_status", table_name="user_service_statuses")
    op.drop_table("user_service_statuses")
    op.drop_table("users")
    # ### end Alembic commands ###