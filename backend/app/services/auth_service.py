from database.auth_db import create_user, get_user_by_username
from utils.security import get_password_hash, verify_password, create_access_token

def register_user(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")
    full_name = user_data.get("full_name", "")

    if not username or not password:
        raise ValueError("Tên đăng nhập và mật khẩu là bắt buộc.")

    if len(password) < 6:
        raise ValueError("Mật khẩu phải chứa ít nhất 6 ký tự.")

    # Check if user exists
    existing_user = get_user_by_username(username)
    if existing_user:
        raise ValueError("Tên đăng nhập đã được sử dụng.")

    # Hash password and create user
    hashed_password = get_password_hash(password)
    success = create_user(username, hashed_password, full_name)
    if not success:
        raise ValueError("Lỗi hệ thống khi tạo tài khoản.")
    
    return {"message": "Đăng ký tài khoản thành công."}

def authenticate_user(user_data: dict):
    username = user_data.get("username")
    password = user_data.get("password")

    if not username or not password:
        raise ValueError("Tên đăng nhập và mật khẩu là bắt buộc.")

    user = get_user_by_username(username)
    if not user:
        raise ValueError("Tên đăng nhập không tồn tại.")

    if not verify_password(password, user["PasswordHash"]):
        raise ValueError("Mật khẩu không chính xác.")

    # Generate JWT Token
    access_token = create_access_token(data={"sub": user["Username"], "id": user["ID_User"]})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user["ID_User"],
            "username": user["Username"],
            "full_name": user["FullName"]
        }
    }
