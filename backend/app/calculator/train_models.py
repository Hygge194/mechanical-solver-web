# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib

def train_bevel_gear_doctor():
    print("==================================================")
    print("🤖 ĐANG HUẤN LUYỆN MÔ HÌNH BÁNH RĂNG CÔN...")
    print("==================================================")
    
    # 1. Đọc dữ liệu từ Bước 1
    try:
        df = pd.read_csv("con_errors.csv")
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file 'con_errors.csv'. Hãy chạy Bước 1 trước!")
        return

    # 2. Phân tách Thuộc tính (X) và Mục tiêu cần dự đoán (y)
    # Các đặc trưng đầu vào khi hệ thống bị lỗi
    X = df[['T1', 'u', 'mte_loi', 'z1', 'HB1', 'overload_ratio']]
    # Nhãn mục tiêu: Module mte đúng cần đạt
    y = df['suggested_mte']

    # 3. Chia dữ liệu thành 2 tập: Train (80%) để học và Test (20%) để đánh giá thử nghiệm
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Khởi tạo thuật toán Random Forest Regressor
    # n_estimators=100: Sử dụng 100 cây quyết định độc lập để bỏ phiếu kết quả
    # max_depth=12: Giới hạn chiều sâu của cây để tránh hiện tượng quá khớp (Overfitting)
    model_con = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    
    # Huấn luyện mô hình
    model_con.fit(X_train, y_train)

    # 5. Đánh giá độ chính xác của mô hình
    y_pred = model_con.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"🔹 Số lượng mẫu huấn luyện: {len(X_train)}")
    print(f"🔹 Sai số tuyệt đối trung bình (MAE): {mae:.4f} mm")
    print(f"🔹 Độ tương thích thuật toán (R² Score): {r2 * 100:.2f}%")

    # 6. Xuất mô hình ra file nhị phân đóng gói (.pkl)
    joblib.dump(model_con, "ai_doctor_con.pkl")
    print("💾 Đã lưu mô hình thành công: 'ai_doctor_con.pkl'\n")


def train_spur_gear_doctor():
    print("==================================================")
    print("🤖 ĐANG HUẤN LUYỆN MÔ HÌNH BÁNH RĂNG TRỤ...")
    print("==================================================")
    
    try:
        df = pd.read_csv("tru_errors.csv")
    except FileNotFoundError:
        print("❌ Lỗi: Không tìm thấy file 'tru_errors.csv'. Hãy chạy Bước 1 trước!")
        return

    # Đối với bánh răng trụ, đầu vào không cần HB1 vì logic file spur_gear.py của bạn 
    # đã tính ứng suất cho phép trực tiếp qua sH_lim từ giao diện đầu vào
    X = df[['T3', 'u', 'm_loi', 'z1', 'overload_ratio']]
    y = df['suggested_m']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model_tru = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    model_tru.fit(X_train, y_train)

    y_pred = model_tru.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    print(f"🔹 Số lượng mẫu huấn luyện: {len(X_train)}")
    print(f"🔹 Sai số tuyệt đối trung bình (MAE): {mae:.4f} mm")
    print(f"🔹 Độ tương thích thuật toán (R² Score): {r2 * 100:.2f}%")

    joblib.dump(model_tru, "ai_doctor_tru.pkl")
    print("💾 Đã lưu mô hình thành công: 'ai_doctor_tru.pkl'\n")

# ─────────────────────────────────────────────────────────────────────────────
# KÍCH HOẠT HUẤN LUYỆN
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    train_bevel_gear_doctor()
    train_spur_gear_doctor()