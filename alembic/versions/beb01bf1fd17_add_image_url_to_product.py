from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine import reflection

# Revision identifiers, used by Alembic.
revision: str = 'beb01bf1fd17'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    bind = op.get_bind()
    inspector = reflection.Inspector.from_engine(bind)
    dialect = bind.dialect.name

    if dialect != 'sqlite':
        # Handle foreign key constraints for databases that support them
        with op.batch_alter_table('buyers', schema=None) as batch_op:
            batch_op.drop_constraint('fk_buyers_user_id', type_='foreignkey')
            batch_op.create_foreign_key(
                'fk_buyers_user_id',
                'users',
                ['user_id'],
                ['id'],
                ondelete='CASCADE'
            )

        with op.batch_alter_table('farmers', schema=None) as batch_op:
            batch_op.drop_constraint('fk_farmers_user_id', type_='foreignkey')
            batch_op.create_foreign_key(
                'fk_farmers_user_id',
                'users',
                ['user_id'],
                ['id'],
                ondelete='CASCADE'
            )
    else:
        # SQLite does not support dropping constraints by name
        # If you need to enforce ON DELETE CASCADE, consider recreating the table
        # Alternatively, ensure that foreign key constraints are defined with ON DELETE CASCADE from the start
        pass  # Skip altering constraints for SQLite

    # Adding a new column (supported by SQLite)
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=255), nullable=True))

def downgrade() -> None:
    bind = op.get_bind()
    inspector = reflection.Inspector.from_engine(bind)
    dialect = bind.dialect.name

    # Reverse the upgrade steps

    # Removing the added column
    with op.batch_alter_table('products', schema=None) as batch_op:
        batch_op.drop_column('image_url')

    if dialect != 'sqlite':
        # Reverse foreign key constraints for other databases
        with op.batch_alter_table('farmers', schema=None) as batch_op:
            batch_op.drop_constraint('fk_farmers_user_id', type_='foreignkey')
            batch_op.create_foreign_key(
                'fk_farmers_user_id',
                'users',
                ['user_id'],
                ['id']
            )

        with op.batch_alter_table('buyers', schema=None) as batch_op:
            batch_op.drop_constraint('fk_buyers_user_id', type_='foreignkey')
            batch_op.create_foreign_key(
                'fk_buyers_user_id',
                'users',
                ['user_id'],
                ['id']
            )
    else:
        # Skip altering constraints for SQLite
        pass
