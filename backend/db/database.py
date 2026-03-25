from sqlalchemy import create_engine, MetaData, text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.config import Config

engine = create_engine(Config.DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)
    # Ensure `email` column exists on users table for older databases
    try:
        inspector = inspect(engine)
        if 'users' in inspector.get_table_names():
            cols = [c['name'] for c in inspector.get_columns('users')]

            # map of column -> SQL definition to add if missing
            # Use PostgreSQL-compatible column definitions and use
            # `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` where possible.
            expected_cols = {
                'email': "VARCHAR(100)",
                'first_name': "VARCHAR(50)",
                'last_name': "VARCHAR(50)",
                'phone': "VARCHAR(20)",
                'is_active': "BOOLEAN DEFAULT TRUE",
                'role': "VARCHAR(20) DEFAULT 'user'"
            }

            with engine.connect() as conn:
                for col, definition in expected_cols.items():
                    if col not in cols:
                        try:
                            # Use IF NOT EXISTS for Postgres (no-op if already present)
                            conn.execute(text(f"ALTER TABLE users ADD COLUMN IF NOT EXISTS {col} {definition}"))
                        except Exception:
                            # best-effort; continue adding other columns
                            pass

                # create index for email if not present (Postgres supports IF NOT EXISTS)
                try:
                    conn.execute(text("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)"))
                except Exception:
                    pass
    except Exception:
        # Fail silently here; calling code will still detect schema drift and log appropriately
        pass