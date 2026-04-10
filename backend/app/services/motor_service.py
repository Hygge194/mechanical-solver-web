from calculator.motor import tinh_HieuSuat_Tong, tinh_P_can_thiet, tinh_n_so_bo, tinh_thong_so_truc, tinh_toan_he_thong_thuc_te
from database.mysql_db import fetch_motor_by_power_and_speed

def get_motor_recommendations(data):
    # 2.1.2: Xác định công suất cần thiết
    hieu_suat = data.get('hieu_suat', {})
    eta_t = tinh_HieuSuat_Tong(
        hieu_suat_dai=hieu_suat.get('dai', 0.96),
        hieu_suat_con=hieu_suat.get('con', 0.97),
        hieu_suat_tru=hieu_suat.get('tru', 0.98),
        hieu_suat_o_lan=hieu_suat.get('o_lan', 0.995),
        hieu_suat_khop_noi=hieu_suat.get('khop_noi', 0.99)
    )
    
    K = data.get('he_so_tai', 1.0)
    p_ct = tinh_P_can_thiet(data.get('p_tai_w', 0), eta_t, K)
    
    # 2.1.3: Xác định số vòng quay sơ bộ
    n_lv = data.get('n_lv', 100)
    n_sb, u_t_sb = tinh_n_so_bo(n_lv)
    
    # 2.1.4: Tra bảng và chọn quy cách
    motors = fetch_motor_by_power_and_speed(p_ct, n_sb)
    
    # Tự động phân bổ tỉ số truyền cho động cơ đầu tiên
    ti_so_truyen = {}
    if len(motors) > 0:
        dc_chon_db = motors[0]
        # Tạo format JSON mong đợi từ tinh_toan_he_thong_thuc_te
        dc_chon = {
            'VanToc_vph': dc_chon_db['n'],
            'Model': dc_chon_db['code']
        }
        ti_so_truyen = tinh_toan_he_thong_thuc_te(dc_chon, n_lv)
        
    return {
        "muc_2_1_2": {"p_ct": round(p_ct, 3), "eta": round(eta_t, 3)},
        "muc_2_1_3": {"n_sb": round(n_sb, 2), "u_t_sb": u_t_sb},
        "muc_2_1_4_goi_y": motors,
        "phan_bo_ti_so": ti_so_truyen
    }

def finalize_chapter_2(selected_motor, ratios, efficiency_data):
    result = tinh_thong_so_truc(selected_motor['P'], selected_motor['n'], ratios, efficiency_data)
    
    return {
        "status": "Chương 2 hoàn tất",
        "bang_dong_hoc": result
    }