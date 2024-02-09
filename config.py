import os, logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Global variables
project_root = os.getcwd()
logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL")
