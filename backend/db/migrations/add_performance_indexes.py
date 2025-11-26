"""
Database Performance Indexes Migration

This migration adds indexes to improve query performance without changing
the existing table structure or data.

Usage:
    python -m backend.db.migrations.add_performance_indexes
"""

import sys
import logging
from sqlalchemy import create_engine, text, inspect
from backend.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_index_exists(engine, table_name: str, index_name: str) -> bool:
    """Check if an index already exists"""
    inspector = inspect(engine)
    indexes = inspector.get_indexes(table_name)
    return any(idx['name'] == index_name for idx in indexes)


def add_indexes(engine):
    """Add performance indexes to database"""
    
    indexes_to_create = [
        # Users table indexes
        {
            "table": "users",
            "name": "idx_users_username",
            "columns": ["username"],
            "description": "Fast user lookup by username (for login)"
        },
        {
            "table": "users",
            "name": "idx_users_email",
            "columns": ["email"],
            "description": "Fast user lookup by email (for password reset)"
        },
        {
            "table": "users",
            "name": "idx_users_role_active",
            "columns": ["role_id", "is_active"],
            "description": "Fast filtering by role and active status"
        },
        {
            "table": "users",
            "name": "idx_users_last_activity",
            "columns": ["last_activity"],
            "description": "Fast sorting by last activity (for admin dashboard)"
        },
        
        # Comments table indexes
        {
            "table": "comments",
            "name": "idx_comments_platform",
            "columns": ["platform"],
            "description": "Fast filtering by platform (Facebook, YouTube, Twitter)"
        },
        {
            "table": "comments",
            "name": "idx_comments_prediction",
            "columns": ["prediction"],
            "description": "Fast filtering by prediction category"
        },
        {
            "table": "comments",
            "name": "idx_comments_user_created",
            "columns": ["user_id", "created_at"],
            "description": "Fast user-specific comment queries with date sorting"
        },
        {
            "table": "comments",
            "name": "idx_comments_platform_pred_created",
            "columns": ["platform", "prediction", "created_at"],
            "description": "Composite index for common filter combinations"
        },
        {
            "table": "comments",
            "name": "idx_comments_created_at",
            "columns": ["created_at"],
            "description": "Fast date range queries and sorting"
        },
        {
            "table": "comments",
            "name": "idx_comments_confidence",
            "columns": ["confidence"],
            "description": "Fast filtering by confidence threshold"
        },
        {
            "table": "comments",
            "name": "idx_comments_is_reviewed",
            "columns": ["is_reviewed"],
            "description": "Fast filtering for manual review queue"
        },
        
        # Logs table indexes
        {
            "table": "logs",
            "name": "idx_logs_timestamp",
            "columns": ["timestamp"],
            "description": "Fast date range queries and sorting"
        },
        {
            "table": "logs",
            "name": "idx_logs_user_timestamp",
            "columns": ["user_id", "timestamp"],
            "description": "Fast user-specific activity logs"
        },
        {
            "table": "logs",
            "name": "idx_logs_action",
            "columns": ["action"],
            "description": "Fast filtering by action type"
        },
        {
            "table": "logs",
            "name": "idx_logs_resource",
            "columns": ["resource", "resource_id"],
            "description": "Fast lookup by resource"
        },
        
        # Reports table indexes
        {
            "table": "reports",
            "name": "idx_reports_status",
            "columns": ["status"],
            "description": "Fast filtering by report status"
        },
        {
            "table": "reports",
            "name": "idx_reports_type",
            "columns": ["report_type"],
            "description": "Fast filtering by report type"
        },
        {
            "table": "reports",
            "name": "idx_reports_user_created",
            "columns": ["user_id", "created_at"],
            "description": "Fast user-specific reports"
        },
        {
            "table": "reports",
            "name": "idx_reports_comment",
            "columns": ["comment_id"],
            "description": "Fast lookup of reports for a comment"
        },
        
        # RefreshTokens table indexes
        {
            "table": "refresh_tokens",
            "name": "idx_refresh_tokens_token",
            "columns": ["token"],
            "description": "Fast token lookup"
        },
        {
            "table": "refresh_tokens",
            "name": "idx_refresh_tokens_user",
            "columns": ["user_id"],
            "description": "Fast user token lookup"
        },
        {
            "table": "refresh_tokens",
            "name": "idx_refresh_tokens_expires",
            "columns": ["expires_at"],
            "description": "Fast expired token cleanup"
        },
    ]
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    with engine.connect() as conn:
        for idx_def in indexes_to_create:
            table = idx_def["table"]
            name = idx_def["name"]
            columns = idx_def["columns"]
            description = idx_def["description"]
            
            try:
                # Check if index already exists
                if check_index_exists(engine, table, name):
                    logger.info(f"⏭️  Skipping {name} - already exists")
                    skipped_count += 1
                    continue
                
                # Create index
                columns_str = ", ".join(columns)
                sql = f"CREATE INDEX {name} ON {table} ({columns_str})"
                
                logger.info(f"📊 Creating index: {name}")
                logger.info(f"   Table: {table}")
                logger.info(f"   Columns: {columns_str}")
                logger.info(f"   Purpose: {description}")
                
                conn.execute(text(sql))
                conn.commit()
                
                logger.info(f"✅ Created index: {name}")
                created_count += 1
                
            except Exception as e:
                logger.error(f"❌ Failed to create index {name}: {e}")
                failed_count += 1
                continue
    
    logger.info("\n" + "="*60)
    logger.info(f"📊 Index Creation Summary:")
    logger.info(f"   ✅ Created: {created_count}")
    logger.info(f"   ⏭️  Skipped: {skipped_count}")
    logger.info(f"   ❌ Failed: {failed_count}")
    logger.info(f"   📝 Total: {len(indexes_to_create)}")
    logger.info("="*60)


def remove_indexes(engine):
    """Remove all performance indexes (for rollback)"""
    
    indexes_to_remove = [
        # Users
        "idx_users_role_active",
        "idx_users_last_activity",
        
        # Comments
        "idx_comments_user_created",
        "idx_comments_platform_pred_created",
        "idx_comments_confidence",
        "idx_comments_is_reviewed",
        
        # Logs
        "idx_logs_user_timestamp",
        "idx_logs_resource",
        
        # Reports
        "idx_reports_user_created",
        
        # RefreshTokens
        "idx_refresh_tokens_expires",
    ]
    
    removed_count = 0
    
    with engine.connect() as conn:
        for index_name in indexes_to_remove:
            try:
                sql = f"DROP INDEX IF EXISTS {index_name}"
                conn.execute(text(sql))
                conn.commit()
                logger.info(f"✅ Removed index: {index_name}")
                removed_count += 1
            except Exception as e:
                logger.error(f"❌ Failed to remove index {index_name}: {e}")
    
    logger.info(f"\n✅ Removed {removed_count} indexes")


def main():
    """Main migration function"""
    
    logger.info("="*60)
    logger.info("🚀 Starting Database Performance Index Migration")
    logger.info("="*60)
    logger.info(f"Database URL: {settings.DATABASE_URL}")
    logger.info("")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        
        # Check if we should rollback
        if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
            logger.info("🔄 Rolling back indexes...")
            remove_indexes(engine)
        else:
            logger.info("➕ Adding indexes...")
            add_indexes(engine)
        
        logger.info("\n✅ Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

