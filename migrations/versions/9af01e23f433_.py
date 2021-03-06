"""empty message

Revision ID: 9af01e23f433
Revises: 7ae345483f23
Create Date: 2020-08-03 01:43:37.979097

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9af01e23f433'
down_revision = '7ae345483f23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Artist', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Artist', sa.Column('seeking_venue', sa.Boolean(), nullable=True, default=True))
    op.add_column('Artist', sa.Column('website', sa.String(length=500), nullable=True))
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    op.drop_constraint('Artist_venue_id_fkey', 'Artist', type_='foreignkey')
    op.drop_column('Artist', 'venue_id')
    op.add_column('Venue', sa.Column('seeking_description', sa.String(length=500), nullable=True))
    op.add_column('Venue', sa.Column('seeking_talent', sa.Boolean(), nullable=True, default=True))
    op.add_column('Venue', sa.Column('website', sa.String(length=500), nullable=True))
    op.alter_column('Venue', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('Venue', 'website')
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'seeking_description')
    op.add_column('Artist', sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('Artist_venue_id_fkey', 'Artist', 'Venue', ['venue_id'], ['id'])
    op.alter_column('Artist', 'genres',
               existing_type=sa.VARCHAR(length=120),
               nullable=True)
    op.drop_column('Artist', 'website')
    op.drop_column('Artist', 'seeking_venue')
    op.drop_column('Artist', 'seeking_description')
    # ### end Alembic commands ###
