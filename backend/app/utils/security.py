from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Secret key cho JWT từ .env hoặc mặc định
SECRET_KEY = os.getenv("SECRET_KEY", "19042005")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # Token sống 7 ngày

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def truncate_password_to_72_bytes(pwd: str) -> str:
    # Bcrypt giới hạn tối đa 72 bytes UTF-8 thay vì 72 string thông thường
    encoded = pwd.encode('utf-8')
    return encoded[:72].decode('utf-8', 'ignore')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(truncate_password_to_72_bytes(plain_password), hashed_password)

def get_password_hash(password):
    return pwd_context.hash(truncate_password_to_72_bytes(password))

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
