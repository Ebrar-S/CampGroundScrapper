import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models.db_model import Base 

DATABASE_URL = "postgresql://user:password@localhost:5432/case_study"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Session local to interact with the database
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """
    Initializes the database by creating tables if they do not exist.
    """
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        raise e

# Initialize the database (create tables if they don't exist)
if __name__ == "__main__":
    init_db()
