import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    # Validate connections before use so workers recover automatically when the
    # database (e.g. a paused Supabase project) comes back, without a restart.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all database tables.

    Returns True on success. Never raises: if the database is unreachable at
    startup (e.g. a paused Supabase project), we log and let the app boot anyway
    so /health stays up and requests recover once the DB returns.
    """
    try:
        Base.metadata.create_all(bind=engine)
        return True
    except Exception:
        logger.exception("init_db failed — database unreachable at startup; "
                         "app will boot and serve 503 on DB-backed routes until it recovers")
        return False
