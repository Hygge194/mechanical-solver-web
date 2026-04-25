import mysql.connector
from database.config import DB_CONFIG
from datetime import datetime

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def fetch_motor_by_power(p_min):
    # truy van sql
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT * FROM Thu_Vien_Dong_Co 
        WHERE CongSuat_kW >= %s 
        ORDER BY CongSuat_kW ASC, VanToc_vph DESC 
        LIMIT 5
    """
    cursor.execute(query, (p_min,))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return results

def fetch_motor_by_power_and_speed(p_min, n_sb):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = """
        SELECT ID_DongCo as id, Model as code, CongSuat_kW as P, VanToc_vph as n, CosPhi as cosphi, Tk_Tdn as tk_tdn
        FROM Thu_Vien_Dong_Co 
        WHERE CongSuat_kW >= %s 
        ORDER BY ABS(VanToc_vph - %s) ASC, CongSuat_kW ASC 
        LIMIT 3
    """
    cursor.execute(query, (p_min, n_sb))
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return results


# ================================================================
# HÀM CHECKPOINT – Ghi kết quả từng bước vào M1_Checkpoint
# ================================================================

def checkpoint_init(project_id):
    """
    Khởi tạo 1 dòng trống trong M1_Checkpoint cho dự án.
    Phải gọi đầu tiên trước tất cả các hàm checkpoint_buoc_X().
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Sử dụng INSERT ... ON DUPLICATE KEY UPDATE để tránh lỗi nếu dòng đã tồn tại
        sql = """
            INSERT INTO M1_Checkpoint (ID_DuAn) VALUES (%s)
            ON DUPLICATE KEY UPDATE ID_DuAn = ID_DuAn
        """
        cursor.execute(sql, (project_id,))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"DEBUG: Checkpoint initialized for Project ID {project_id}")
    except Exception as e:
        print(f"ERROR in checkpoint_init: {e}")


def _update_checkpoint(project_id, fields: dict):
    """
    Hàm nội bộ: cập nhật các cột bất kỳ trong M1_Checkpoint.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        set_clause = ", ".join([f"{col} = %s" for col in fields])
        sql = f"UPDATE M1_Checkpoint SET {set_clause} WHERE ID_DuAn = %s"
        values = list(fields.values()) + [project_id]
        
        cursor.execute(sql, values)
        conn.commit()
        
        if cursor.rowcount == 0:
            print(f"WARNING: No rows updated in M1_Checkpoint for project_id {project_id}. Does it exist?")
        else:
            print(f"DEBUG: Updated checkpoint fields {list(fields.keys())} for project_id {project_id}")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"ERROR in _update_checkpoint: {e}")



def checkpoint_buoc1(project_id, eta_dai, eta_con, eta_tru, eta_o_lan, eta_khop_noi, eta_tong):
    """Bước 1: Lưu kết quả tinh_HieuSuat_Tong()"""
    _update_checkpoint(project_id, {
        "eta_dai":      eta_dai,
        "eta_con":      eta_con,
        "eta_tru":      eta_tru,
        "eta_o_lan":    eta_o_lan,
        "eta_khop_noi": eta_khop_noi,
        "eta_tong":     eta_tong,
        "buoc1_ok":     True,
        "buoc1_ts":     datetime.now(),
    })


def checkpoint_buoc2(project_id, P_tai_W, K_tai, P_can_thiet_kW):
    """Bước 2: Lưu kết quả tinh_P_can_thiet()"""
    _update_checkpoint(project_id, {
        "P_tai_W":        P_tai_W,
        "K_tai":          K_tai,
        "P_can_thiet_kW": P_can_thiet_kW,
        "buoc2_ok":       True,
        "buoc2_ts":       datetime.now(),
    })


def checkpoint_buoc3(project_id, n_lv, u_dai_sb, u_hgt_sb, u_t_so_bo, n_so_bo):
    """Bước 3: Lưu kết quả tinh_n_so_bo()"""
    _update_checkpoint(project_id, {
        "n_lv_vph":    n_lv,
        "u_dai_sb":    u_dai_sb,
        "u_hgt_sb":    u_hgt_sb,
        "u_t_so_bo":   u_t_so_bo,
        "n_so_bo_vph": n_so_bo,
        "buoc3_ok":    True,
        "buoc3_ts":    datetime.now(),
    })


def checkpoint_buoc4(project_id, model, P_dc, n_dc):
    """Bước 4: Lưu động cơ đã chọn"""
    _update_checkpoint(project_id, {
        "dong_co_chon":  model,
        "P_dong_co_kW":  P_dc,
        "n_dong_co_vph": n_dc,
        "buoc4_ok":      True,
        "buoc4_ts":      datetime.now(),
    })


def checkpoint_buoc5(project_id, u_t, u_dai, u_h, u1, u2):
    """Bước 5: Lưu kết quả tinh_toan_he_thong_thuc_te()"""
    _update_checkpoint(project_id, {
        "u_t_thuc_te": u_t,
        "u_dai_thuc":  u_dai,
        "u_hop_so":    u_h,
        "u1_con":      u1,
        "u2_tru":      u2,
        "buoc5_ok":    True,
        "buoc5_ts":    datetime.now(),
    })


def checkpoint_buoc6(project_id, kin, motor_id=None):
    """Bước 6: Lưu bảng động lực học tinh_thong_so_truc() và ID_DongCo chính thức"""
    dc  = kin.get('truc_dc', {})
    t1  = kin.get('truc_1',  {})
    t2  = kin.get('truc_2',  {})
    t3  = kin.get('truc_3',  {})
    _update_checkpoint(project_id, {
        "P_dc": dc.get('P'), "n_dc": dc.get('n'), "T_dc": dc.get('T'),
        "P1":   t1.get('P'), "n1":   t1.get('n'), "T1":   t1.get('T'),
        "P2":   t2.get('P'), "n2":   t2.get('n'), "T2":   t2.get('T'),
        "P3":   t3.get('P'), "n3":   t3.get('n'), "T3":   t3.get('T'),
        "buoc6_ok": True,
        "buoc6_ts": datetime.now(),
        "ID_DongCo_Chon": motor_id,
        "Status_Valid": True
    })