from calculator.motor import tinh_HieuSuat_Tong, tinh_P_can_thiet, tinh_n_so_bo, tinh_thong_so_truc, tinh_toan_he_thong_thuc_te
from database.mysql_db import (
    fetch_motor_by_power_and_speed,
    checkpoint_init,
    checkpoint_buoc1,
    checkpoint_buoc2,
    checkpoint_buoc3,
    checkpoint_buoc4,
    checkpoint_buoc5,
    checkpoint_buoc6,
)

def get_motor_recommendations(data, project_id=None):
    """
    project_id: nếu truyền vào thì mỗi bước tính xong sẽ ghi ngay vào M1_Checkpoint.
                Nếu None thì chạy bình thường, không ghi checkpoint.
    """
    hieu_suat = data.get('hieu_suat', {})

    # Lấy các giá trị input hiệu suất
    eta_dai      = hieu_suat.get('dai',       0.96)
    eta_con      = hieu_suat.get('con',       0.97)
    eta_tru      = hieu_suat.get('tru',       0.98)
    eta_o_lan    = hieu_suat.get('o_lan',     0.995)
    eta_khop_noi = hieu_suat.get('khop_noi', 0.99)

    # Khởi tạo dòng checkpoint (nếu có project_id)
    if project_id:
        checkpoint_init(project_id)

    # ── BƯỚC 1: Hiệu suất tổng ───────────────────────────────
    eta_t = tinh_HieuSuat_Tong(eta_dai, eta_con, eta_tru, eta_o_lan, eta_khop_noi)
    if project_id:
        checkpoint_buoc1(project_id, eta_dai, eta_con, eta_tru, eta_o_lan, eta_khop_noi, eta_t)

    # ── BƯỚC 2: Công suất cần thiết ──────────────────────────
    K          = data.get('he_so_tai', 1.0)
    p_tai_w    = data.get('p_tai_w', 0)
    p_ct       = tinh_P_can_thiet(p_tai_w, eta_t, K)
    if project_id:
        checkpoint_buoc2(project_id, p_tai_w, K, p_ct)

    # ── BƯỚC 3: Tốc độ sơ bộ ────────────────────────────────
    n_lv          = data.get('n_lv', 100)
    u_dai_sb      = 4
    u_hgt_sb      = 10
    n_sb, u_t_sb  = tinh_n_so_bo(n_lv, u_dai_sb, u_hgt_sb)
    if project_id:
        checkpoint_buoc3(project_id, n_lv, u_dai_sb, u_hgt_sb, u_t_sb, n_sb)

    # ── BƯỚC 4: Tra bảng chọn động cơ ───────────────────────
    motors = fetch_motor_by_power_and_speed(p_ct, n_sb)
    if project_id and motors:
        m = motors[0]  # Động cơ đứng đầu (tốt nhất)
        checkpoint_buoc4(project_id, m['code'], m['P'], m['n'])

    # ── BƯỚC 5: Phân phối tỉ số truyền ──────────────────────
    ti_so_truyen = {}
    if motors:
        dc_chon = {'VanToc_vph': motors[0]['n'], 'Model': motors[0]['code']}
        ti_so_truyen = tinh_toan_he_thong_thuc_te(dc_chon, n_lv)
        if project_id:
            checkpoint_buoc5(
                project_id,
                ti_so_truyen['u_t'],
                ti_so_truyen['u_dai'],
                ti_so_truyen['u_t'] / ti_so_truyen['u_dai'],  # u_h
                ti_so_truyen['u_1'],
                ti_so_truyen['u_2'],
            )

    return {
        "muc_2_1_2": {"p_ct": round(p_ct, 3), "eta": round(eta_t, 3)},
        "muc_2_1_3": {"n_sb": round(n_sb, 2), "u_t_sb": u_t_sb},
        "muc_2_1_4_goi_y": motors,
        "phan_bo_ti_so": ti_so_truyen
    }


def finalize_m1_with_checkpoint(selected_motor, ratios, efficiency_data, project_id=None):
    """
    Được gọi khi người dùng bấm "Chọn động cơ" ở Bước 2.
    Tính bảng động lực học và ghi Checkpoint Bước 6.
    """
    result = tinh_thong_so_truc(
        selected_motor['P'], selected_motor['n'],
        [ratios['u_dai'], ratios['u_1'], ratios['u_2']],
        efficiency_data
    )

    # ── BƯỚC 5 & 6: Cập nhật tỉ số truyền thực tế và Bảng động lực học ──
    if project_id:
        # Cập nhật bước 5 với tỉ số thực tế của motor đã chọn
        checkpoint_buoc5(
            project_id,
            ratios['u_t'],
            ratios['u_dai'],
            ratios['u_t'] / ratios['u_dai'],  # u_h
            ratios['u_1'],
            ratios['u_2']
        )
        motor_id = selected_motor.get('id')
        checkpoint_buoc6(project_id, result, motor_id=motor_id)

    return {
        "status": "M1 hoàn tất",
        "bang_dong_hoc": result
    }


def finalize_chapter_2(selected_motor, ratios, efficiency_data):
    result = tinh_thong_so_truc(selected_motor['P'], selected_motor['n'], ratios, efficiency_data)
    return {"status": "Chương 2 hoàn tất", "bang_dong_hoc": result}