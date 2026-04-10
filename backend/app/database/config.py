import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mechanical_solver_db"),
    "port": int(os.getenv("DB_PORT", 3306))
}
