import sys
import os

# Thêm thư mục app vào hệ thống để Python tìm thấy các module
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from calculator.motor import tinh_eta_tong, tinh_P_can_thiet, tinh_n_so_bo

def run_test():
    print("--- KIỂM TRA LOGIC CHƯƠNG 2 ---")
    
    # 1. Thông số đầu vào (Lấy đúng theo file Thuyết minh mẫu của bạn)
    P_tai = 5500  # Watts
    n_lv = 70     # v/ph
    

    # 2. Chạy test Mục 2.1.2 (Công suất)
    eta_t = tinh_eta_tong()
    p_ct = tinh_P_can_thiet(P_tai, eta_t)
    
    print(f"[2.1.2] Hiệu suất tổng eta_t: {eta_t:.4f}")
    print(f"[2.1.2] Công suất cần thiết P_ct: {p_ct:.3f} kW")

    # 3. Chạy test Mục 2.1.3 (Vòng quay sơ bộ)
    n_sb, u_t_sb = tinh_n_so_bo(n_lv)
    print(f"[2.1.3] Tỉ số truyền sơ bộ u_t_sb: {u_t_sb}")
    print(f"[2.1.3] Số vòng quay sơ bộ n_sb: {n_sb:.2f} v/ph")
    
    print("-------------------------------")
    print("=> Hãy so sánh các số trên với trang 14-15 trong file PDF của bạn.")

if __name__ == "__main__":
    run_test()