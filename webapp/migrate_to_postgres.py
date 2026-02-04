"""
Migrate data from local SQLite database to PostgreSQL.
Usage: DATABASE_URL="postgresql://user:pass@host/db" python migrate_to_postgres.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database import (
    Base, Application, QuestionnaireAnswer, MeetingTranscript,
    TranscriptAnswer, DavidNote, SynergyScore, Insight,
    AppInsight, PortfolioInsight, CustomWeight, QAHistory
)

# All models in dependency order (parents before children)
MODELS = [
    Application,
    QuestionnaireAnswer,
    MeetingTranscript,
    TranscriptAnswer,
    DavidNote,
    SynergyScore,
    Insight,
    AppInsight,
    PortfolioInsight,
    CustomWeight,
    QAHistory,
]


def migrate():
    pg_url = os.getenv("DATABASE_URL")
    if not pg_url:
        print("ERROR: Set DATABASE_URL environment variable to your PostgreSQL connection string.")
        print('Example: DATABASE_URL="postgresql://user:pass@host/dbname" python migrate_to_postgres.py')
        sys.exit(1)

    if pg_url.startswith("postgres://"):
        pg_url = pg_url.replace("postgres://", "postgresql://", 1)

    # Source: local SQLite
    sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "avangrid.db")
    if not os.path.exists(sqlite_path):
        print(f"ERROR: SQLite database not found at {sqlite_path}")
        sys.exit(1)

    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}", echo=False)
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()

    # Target: PostgreSQL
    pg_engine = create_engine(pg_url, echo=False)
    PgSession = sessionmaker(bind=pg_engine)

    # Create all tables in PostgreSQL
    print("Creating tables in PostgreSQL...")
    Base.metadata.create_all(pg_engine)

    pg_session = PgSession()

    try:
        total = 0
        for model in MODELS:
            table_name = model.__tablename__
            rows = sqlite_session.query(model).all()

            if not rows:
                print(f"  {table_name}: 0 rows (skipped)")
                continue

            # Check if target already has data
            existing = pg_session.query(model).count()
            if existing > 0:
                print(f"  {table_name}: {existing} rows already exist in PostgreSQL, skipping (use --force to overwrite)")
                continue

            # Get column names from the model
            mapper = inspect(model)
            columns = [c.key for c in mapper.column_attrs]

            count = 0
            for row in rows:
                data = {col: getattr(row, col) for col in columns}
                new_obj = model(**data)
                pg_session.merge(new_obj)
                count += 1

            pg_session.commit()
            total += count
            print(f"  {table_name}: {count} rows migrated")

        print(f"\nMigration complete! {total} total rows migrated to PostgreSQL.")

    except Exception as e:
        pg_session.rollback()
        print(f"\nERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        sqlite_session.close()
        pg_session.close()


if __name__ == "__main__":
    migrate()
