"""Add TERMINATED status to ApprovalStatusEnum

Revision ID: c98c1b3e1c84
Revises: b2c858db071e
Create Date: 2025-09-11 18:38:30.703077

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c98c1b3e1c84'
down_revision = 'b2c858db071e'
branch_labels = None
depends_on = None


def upgrade():
    # Add TERMINATED to the enum values for the status column
    op.execute("ALTER TABLE user_request MODIFY COLUMN status ENUM('PENDING', 'APPROVED', 'REJECTED', 'TERMINATED') NOT NULL")


def downgrade():
    # Remove TERMINATED from the enum values (this will fail if any records have TERMINATED status)
    op.execute("ALTER TABLE user_request MODIFY COLUMN status ENUM('PENDING', 'APPROVED', 'REJECTED') NOT NULL")
