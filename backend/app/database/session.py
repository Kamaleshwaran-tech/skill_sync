from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from app.config.settings import get_settings
from app.database.base import Base

settings = get_settings()


def get_database_url():
    url = settings.database_url
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    elif url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    return url


url = get_database_url()
engine = create_engine(
    url,
    echo=settings.db_echo,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False, "timeout": 15}
    if url.startswith("sqlite")
    else {},
)
if url.startswith("sqlite"):

    @event.listens_for(engine, "connect")
    def sqlite_foreign_keys(connection, record):
        connection.execute("PRAGMA foreign_keys=ON")


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db_session():
    with SessionLocal() as db:
        yield db


def check_database_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Database connection successful."
    except Exception:
        return False, "Configured database unavailable."
