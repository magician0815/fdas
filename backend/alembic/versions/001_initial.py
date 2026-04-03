"""初始表结构

Revision ID: 001_initial
Revises: None
Create Date: 2026-04-03

Author: FDAS Team
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库."""
    # 创建uuid扩展
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    # users表
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_users_username', 'users', ['username'], unique=True)

    # sessions表
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_data', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_sessions_expires_at', 'sessions', ['expires_at'])

    # datasources表
    op.create_table(
        'datasources',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, server_default='akshare'),
        sa.Column('config', postgresql.JSONB, nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )

    # collection_tasks表
    op.create_table(
        'collection_tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('datasource_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('datasources.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_data', sa.String(100), nullable=False),
        sa.Column('cron_expression', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('last_run_at', sa.DateTime(timezone=True)),
        sa.Column('next_run_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    op.create_index('idx_collection_tasks_datasource_id', 'collection_tasks', ['datasource_id'])

    # fx_data表
    op.create_table(
        'fx_data',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()'), primary_key=True),
        sa.Column('symbol', sa.String(20), nullable=False),
        sa.Column('date', sa.Date, nullable=False),
        sa.Column('open', sa.Numeric(10, 4)),
        sa.Column('high', sa.Numeric(10, 4)),
        sa.Column('low', sa.Numeric(10, 4)),
        sa.Column('close', sa.Numeric(10, 4)),
        sa.Column('volume', sa.BigInteger),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('symbol', 'date', name='uq_fx_data_symbol_date'),
    )
    op.create_index('idx_fx_data_symbol', 'fx_data', ['symbol'])
    op.create_index('idx_fx_data_date', 'fx_data', ['date'])

    # apscheduler_jobs表（APScheduler持久化）
    op.create_table(
        'apscheduler_jobs',
        sa.Column('id', sa.String(255), primary_key=True),
        sa.Column('next_run_time', sa.DateTime(timezone=True)),
        sa.Column('job_state', sa.LargeBinary, nullable=False),
    )
    op.create_index('idx_apscheduler_jobs_next_run_time', 'apscheduler_jobs', ['next_run_time'])


def downgrade() -> None:
    """回滚数据库."""
    op.drop_table('apscheduler_jobs')
    op.drop_table('fx_data')
    op.drop_table('collection_tasks')
    op.drop_table('datasources')
    op.drop_table('sessions')
    op.drop_table('users')
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp"')