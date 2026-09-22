"""Database engine, session, and base model setup."""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


# Build database path
db_path = settings.get_data_dir() / "badminton_dataset.db"
DATABASE_URL = f"sqlite:///{db_path.as_posix()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=settings.DEBUG,
)

# Enable WAL mode and foreign keys for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy declarative base."""
    pass


def get_db():
    """FastAPI dependency that provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables if they don't exist and run light migrations."""
    from app.models import project, video, frame, processing_job  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Lightweight migration for SQLite existing tables
    try:
        with engine.connect() as conn:
            cursor = conn.exec_driver_sql("PRAGMA table_info(videos)")
            cols = [row[1] for row in cursor.fetchall()]
            if cols:
                if "extraction_interval" not in cols:
                    conn.exec_driver_sql("ALTER TABLE videos ADD COLUMN extraction_interval FLOAT DEFAULT 2.0")
                if "max_resolution" not in cols:
                    conn.exec_driver_sql("ALTER TABLE videos ADD COLUMN max_resolution INTEGER DEFAULT 1080")
                conn.commit()
    except Exception:
        pass
