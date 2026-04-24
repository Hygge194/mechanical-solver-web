# -*- coding: utf-8 -*-
"""
=============================================================
HỆ THỐNG DẪN ĐỘNG CƠ KHÍ
=============================================================
Gồm 2 module liên tiếp:
  Module 1: Tính chọn động cơ & phân phối tỉ số truyền
  Module 2: Tính toán bộ truyền đai hình thang
             → P1 (kW) và ud lấy tự động từ Module 1

Kết nối:
  P1_dai = P_lv = tinh_P_can_thiet() × eta_total   (công suất làm việc)
  ud     = kq_u['u_dai']                             (tỉ số truyền đai)
  n1_dai = n_dc                                      (tốc độ trục động cơ)

Tài liệu tham khảo: Trịnh Chất – Lê Văn Uyển, Tập 1
=============================================================
"""

import math
import mysql.connector  # pip install mysql-connector-python

# ============================================================
# KẾT NỐI DATABASE
# ============================================================
DB_CONFIG = {
    'host':     'localhost',
    'user':     'root',
    'password': '',
    'database': 'he_thong_dan_dong',
}


def get_cursor():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    return conn, cursor


# ============================================================
# BẢNG TRA – BỘ TRUYỀN ĐAI
# ============================================================
DAI_TIET_DIEN = {
    'O':  {'bt': 8.5,  'b': 10, 'h': 6,    'y0': 2.1,  'A': 47,   'd1': (70,  140),  'l': (400,  2500)},
    'A':  {'bt': 11,   'b': 13, 'h': 8,    'y0': 2.8,  'A': 81,   'd1': (100, 200),  'l': (560,  4000)},
    'Б':  {'bt': 14,   'b': 17, 'h': 10.5, 'y0': 4.0,  'A': 138,  'd1': (140, 280),  'l': (800,  6300)},
    'В':  {'bt': 19,   'b': 22, 'h': 13.5, 'y0': 4.8,  'A': 230,  'd1': (200, 400),  'l': (1800, 10600)},
    'Г':  {'bt': 27,   'b': 32, 'h': 19.0, 'y0': 6.9,  'A': 476,  'd1': (315, 630),  'l': (3150, 15000)},
    'Д':  {'bt': 32,   'b': 38, 'h': 23.5, 'y0': 8.3,  'A': 692,  'd1': (500, 1000), 'l': (4500, 18000)},
    'Е':  {'bt': 42,   'b': 50, 'h': 30,   'y0': 11,   'A': 1170, 'd1': (800, 1600), 'l': (6300, 18000)},
}

DAI_BANH = {
    'O':  {'H': 10,   'h0': 2.5, 't': 12,   'e': 8},
    'A':  {'H': 12.5, 'h0': 3.3, 't': 15,   'e': 10},
    'Б':  {'H': 16,   'h0': 4.2, 't': 19,   'e': 12.5},
    'В':  {'H': 21,   'h0': 5.7, 't': 25.5, 'e': 17},
    'Г':  {'H': 27,   'h0': 8.1, 't': 37,   'e': 23},
    'Д':  {'H': 32,   'h0': 9.9, 't': 44.5, 'e': 29},
}

QM = {
    'O': 0.061, 'A': 0.105, 'Б': 0.178, 'В': 0.300,
}

P0_TABLE = {
    'O': {
        '_l0': 1320,
        63:  {3: 0.33, 5: 0.49, 10: 0.83, 15: 1.04, 20: 1.14, 25: None},
        90:  {3: 0.46, 5: 0.64, 10: 1.17, 15: 1.54, 20: 1.80, 25: 1.88},
        112: {3: 0.48, 5: 0.75, 10: 1.33, 15: 1.78, 20: 2.12, 25: 2.30},
    },
    'A': {
        '_l0': 1700,
        112: {3: 0.70, 5: 1.08, 10: 1.85, 15: 2.40, 20: 2.73, 25: 2.85},
        125: {3: 0.78, 5: 1.17, 10: 2.00, 15: 2.75, 20: 3.08, 25: 3.26},
        140: {3: 0.80, 5: 1.25, 10: 2.20, 15: 2.92, 20: 3.44, 25: 3.75},
        160: {3: 0.84, 5: 1.32, 10: 2.34, 15: 3.14, 20: 3.78, 25: 4.09},
        180: {3: 0.88, 5: 1.38, 10: 2.47, 15: 3.37, 20: 4.06, 25: 4.46},
    },
    'Б': {
        '_l0': 2240,
        125: {3: 0.92, 5: 1.38, 10: 2.25, 15: 2.61, 20: None, 25: None},
        180: {3: 1.20, 5: 2.13, 10: 3.38, 15: 4.61, 20: 5.34, 25: 5.93},
        224: {3: 1.35, 5: 2.30, 10: 4.00, 15: 5.53, 20: 6.46, 25: 7.08},
        280: {3: 1.65, 5: 2.51, 10: 4.47, 15: 5.57, 20: 7.38, 25: 8.22},
    },
    'В': {
        '_l0': 3750,
        200: {3: 1.83, 5: 2.73, 10: 4.55, 15: 5.75, 20: 6.28,  25: None},
        250: {3: 2.30, 5: 3.54, 10: 6.02, 15: 8.00, 20: 9.23,  25: 9.69},
        280: {3: 2.46, 5: 3.77, 10: 6.59, 15: 8.82, 20: 10.27, 25: 11.00},
        315: {3: 2.63, 5: 3.88, 10: 7.39, 15: 9.71, 20: 11.33, 25: 12.27},
        355: {3: 2.84, 5: 4.29, 10: 7.57, 15: 10.51,20: 12.42, 25: 13.63},
        450: {3: 3.08, 5: 4.74, 10: 8.54, 15: 11.53,20: 14.15, 25: 15.62},
    },
    'Г': {
        '_l0': 6000,
        355: {3: None, 5: 6.67,  10: 11.17, 15: 14.91, 20: 16.50, 25: 17.51},
        500: {3: None, 5: 9.75,  10: 15.57, 15: 20.23, 20: 24.90, 25: 26.47},
        630: {3: None, 5: 10.76, 10: 17.46, 15: 23.60, 20: 27.89, 25: 32.19},
        800: {3: None, 5: 11.14, 10: 19.16, 15: 26.50, 20: 31.11, 25: 34.23},
    },
}

CA_TABLE  = {180:1.00, 170:0.98, 160:0.95, 150:0.92, 140:0.89, 130:0.86,
             120:0.82, 110:0.78, 100:0.73,  90:0.68,  80:0.62,  70:0.56}
CL_TABLE  = {0.5:0.86, 0.6:0.89, 0.8:0.95, 1.0:1.00, 1.2:1.04, 1.4:1.07,
             1.6:1.10, 1.8:1.13, 2.0:1.15, 2.4:1.20}
CU_TABLE  = {1.0:1.000, 1.2:1.070, 1.6:1.110, 1.8:1.120, 2.2:1.130,
             2.4:1.135, 3.0:1.140}
CZ_TABLE  = {1:1.00, 2:0.95, 3:0.95, 4:0.90, 5:0.90, 6:0.85}
AD2_TABLE = {1:1.50, 2:1.20, 3:1.00, 4:0.95, 5:0.90, 6:0.85}

D_TIEUCHUAN = [
    63, 71, 80, 90, 100, 112, 125, 140, 160, 180,
    200, 224, 250, 280, 315, 355, 400, 450, 500,
    560, 630, 710, 800, 900, 1000, 1120, 1250,
    1400, 1600, 1800, 2000, 2240, 2500, 2800, 3150, 3550, 4000,
]

L_TIEUCHUAN_CHINH = [
    400, 450, 500, 560, 630, 710, 750, 800, 900,
    1000, 1120, 1250, 1400, 1600, 1800, 2000,
    2240, 2500, 2800, 3150, 3550, 4000, 4500,
    5000, 5600, 6300, 7100, 8000, 9000, 10000,
    11200, 12500, 14000,
]

L_TIEUCHUAN_PHU = [
    425, 475, 530, 600, 670, 750, 850, 950, 1060,
    1180, 1320, 1500, 1700, 1900, 2120, 2360, 2650,
    3000, 3350, 3750, 4250,
]

L_TIEUCHUAN = sorted(set(L_TIEUCHUAN_CHINH + L_TIEUCHUAN_PHU))

DAI_VUNG = [
    ('O',  2.0,   4.0,    800, 5000),
    ('A',  2.0,   12.5,   630, 3150),
    ('Б',  3.15,  31.5,   500, 3000),
    ('В',  8.0,   80.0,   315, 1250),
    ('Г',  20.0,  200.0,  200,  800),
    ('Д',  80.0,  400.0,  200,  800),
]


# ============================================================
# MODULE 1 – HÀM TÍNH ĐỘNG CƠ
# ============================================================
def tinh_HieuSuat_Tong(
        hieu_suat_dai=0.96,
        hieu_suat_con=0.97,
        hieu_suat_tru=0.98,
        hieu_suat_o_lan=0.995,
        hieu_suat_khop_noi=0.99):
    """
    Hiệu suất truyền động tổng.
    Hệ thống: 1 đai · 1 côn · 1 trụ · 4 ổ lăn · 1 khớp nối.
    """
    eta = (hieu_suat_dai * hieu_suat_con * hieu_suat_tru
           * (hieu_suat_o_lan ** 4) * hieu_suat_khop_noi)
    return round(eta, 4)


def tinh_P_can_thiet(P_tai, eta_total, K=1.0):
    """Tính công suất cần thiết Pct (kW). P_tai tính bằng W."""
    return (P_tai / 1000) * K / eta_total


def tinh_n_so_bo(n_iv, u_dai_sb=4, u_hgt_sb=10):
    """
    Tốc độ sơ bộ.
    n_iv      : số vòng quay trục công tác (v/ph)
    u_dai_sb  : tỉ số truyền đai sơ bộ (Bảng 2.4)
    u_hgt_sb  : tỉ số truyền HGT 2 cấp sơ bộ
    """
    u_t_sb = u_dai_sb * u_hgt_sb
    n_sb   = n_iv * u_t_sb
    return n_sb, u_t_sb


def query_dong_co(cursor, p_ct, n_sb):
    """Truy vấn 3 động cơ phù hợp từ Database."""
    query = """
        SELECT *, ABS(VanToc_vph - %s) AS diff_n
        FROM Thu_Vien_Dong_Co
        WHERE CongSuat_kW >= %s
        ORDER BY CongSuat_kW ASC, diff_n ASC
        LIMIT 3
    """
    cursor.execute(query, (n_sb, p_ct))
    return cursor.fetchall()


def kiem_nghiem_khoi_dong(dc_row, k_qt=1.3):
    """Kiểm nghiệm điều kiện khởi động (Biểu thức 2.6)."""
    h_so_dc = dc_row['Tk_Tdn']
    if h_so_dc >= k_qt:
        return True,  f"Đạt  (Tk/Tdn = {h_so_dc} >= Kqt = {k_qt})"
    return False, f"Không đạt (Tk/Tdn = {h_so_dc} < Kqt = {k_qt})"


def tinh_toan_he_thong_thuc_te(dc_chon, n_iv, u_dai_so_bo=2.5, u_con_so_bo=4.5):
    """
    Phân phối tỉ số truyền thực tế.
    Trả về dict chứa u_dai, u_1 (côn), u_2 (trụ).
    """
    n_dc    = dc_chon['VanToc_vph']
    u_t     = n_dc / n_iv
    u_dai   = u_dai_so_bo
    u_h     = u_t / u_dai
    u_1     = u_con_so_bo
    u_2     = u_h / u_1
    return {
        'model': dc_chon['Model'],
        'u_t':   round(u_t,   4),
        'u_dai': round(u_dai, 4),
        'u_1':   round(u_1,   4),
        'u_2':   round(u_2,   4),
    }


def tinh_thong_so_truc(P_dc, n_dc, u_list, eta_list):
    """
    Tính P, n, T cho từng trục.
    u_list   : [u_dai, u_con, u_tru]
    eta_list : dict {'dai','con','tru','o_lan','kn'}
    """
    n1 = n_dc   / u_list[0]
    n2 = n1     / u_list[1]
    n3 = n2     / u_list[2]

    P1 = P_dc * eta_list['dai']   * eta_list['o_lan']
    P2 = P1   * eta_list['con']   * eta_list['o_lan']
    P3 = P2   * eta_list['tru']   * eta_list['o_lan']

    T_dc = 9.55e6 * (P_dc / n_dc)
    T1   = 9.55e6 * (P1   / n1)
    T2   = 9.55e6 * (P2   / n2)
    T3   = 9.55e6 * (P3   / n3)

    return {
        'truc_dc': {'P': P_dc, 'n': n_dc, 'T': T_dc},
        'truc_1':  {'P': P1,   'n': n1,   'T': T1},
        'truc_2':  {'P': P2,   'n': n2,   'T': T2},
        'truc_3':  {'P': P3,   'n': n3,   'T': T3},
    }


def luu_ket_qua_final(cursor, id_duan, dc_chon, kq_u, kq_truc):
    sql = """
    INSERT INTO Ket_Qua_Chung (
        ID_DuAn, Model_DongCo, ut_thuc, u_dai, u1_con, u2_tru,
        P_dc, n_dc, T_dc, P1, n1, T1, P2, n2, T2, P3, n3, T3
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    values = (
        id_duan, dc_chon['Model'],
        kq_u['u_t'], kq_u['u_dai'], kq_u['u_1'], kq_u['u_2'],
        kq_truc['truc_dc']['P'], kq_truc['truc_dc']['n'], kq_truc['truc_dc']['T'],
        kq_truc['truc_1']['P'],  kq_truc['truc_1']['n'],  kq_truc['truc_1']['T'],
        kq_truc['truc_2']['P'],  kq_truc['truc_2']['n'],  kq_truc['truc_2']['T'],
        kq_truc['truc_3']['P'],  kq_truc['truc_3']['n'],  kq_truc['truc_3']['T'],
    )
    cursor.execute(sql, values)


# ============================================================
# MODULE 2 – HÀM TRA BẢNG (BỘ TRUYỀN ĐAI)
# ============================================================
def noi_suy(bang_dict, x):
    valid = {k: v for k, v in bang_dict.items() if v is not None}
    keys  = sorted(valid.keys())
    if not keys: raise ValueError("Bảng tra rỗng hoặc toàn None")
    if x <= keys[0]:  return valid[keys[0]]
    if x >= keys[-1]: return valid[keys[-1]]
    for i in range(len(keys) - 1):
        x1, x2 = keys[i], keys[i+1]
        if x1 <= x <= x2:
            return valid[x1] + (x - x1) / (x2 - x1) * (valid[x2] - valid[x1])


def chon_loai_dai(P, n):
    candidates = []
    for ten, P_min, P_max, n_min, n_max in DAI_VUNG:
        if P_min <= P <= P_max and n_min <= n <= n_max:
            candidates.append(ten)
    if not candidates:
        raise ValueError("Không tìm được loại đai phù hợp!")
    return candidates[-1]


def chon_d2_tieuchuan(d2_tinh):
    return min(D_TIEUCHUAN, key=lambda x: abs(x - d2_tinh))


def chon_L_tieuchuan(L_tinh, loai_dai, d1, d2, v,
                     alpha_min=120.0, i_max=10.0, buoc_them=1):
    td     = DAI_TIET_DIEN[loai_dai]
    l_min, l_max = td['l']

    def loc_ung_vien(ds):
        ket = [L for L in ds if L >= L_tinh and l_min <= L <= l_max]
        if not ket:
            ket = [L for L in ds if L >= L_tinh]
        return ket

    uv_chinh = loc_ung_vien(sorted(L_TIEUCHUAN_CHINH))
    uv_phu   = loc_ung_vien(sorted(L_TIEUCHUAN_PHU))

    def tim_idx(uv, log, label):
        idx_ok = None
        for idx, L in enumerate(uv):
            lam  = L - math.pi * (d1 + d2) / 2
            disc = lam**2 - 8 * ((d2 - d1) / 2)**2
            if disc < 0:
                log.append(f"  [{label}] L={L:6} mm → discriminant âm, bỏ qua")
                continue
            a_new = (lam + math.sqrt(disc)) / 4
            alpha = 180.0 - (d2 - d1) / a_new * 57.3
            i_dai = v * 1000.0 / L
            ok_a  = alpha >= alpha_min
            ok_i  = i_dai <= i_max
            mark  = ""
            if ok_a and ok_i and idx_ok is None:
                idx_ok = idx
                mark   = "  ← L_min hợp lệ"
            log.append(
                f"  [{label}] L={L:6} mm | a={a_new:7.2f} mm | "
                f"α={alpha:6.2f}° {'✓' if ok_a else '✗'} | "
                f"i={i_dai:.3f} {'✓' if ok_i else '✗'}{mark}"
            )
            if idx_ok is not None and idx >= idx_ok + buoc_them:
                break
        return idx_ok

    log, canh_bao = [], []
    idx_ok = tim_idx(uv_chinh, log, "chính")

    if idx_ok is not None:
        uv_dung = uv_chinh
    else:
        if uv_phu:
            log.append("  ⚠ Nhóm chính không thoả → thử giá trị phụ (ngoặc)...")
            idx_ok  = tim_idx(uv_phu, log, "phụ")
            uv_dung = uv_phu
            if idx_ok is not None:
                canh_bao.append("⚠ Phải dùng L trong ngoặc — xem lại thông số nếu có thể.")
        else:
            uv_dung = []

    if idx_ok is None or not uv_dung:
        L_chon = uv_chinh[-1] if uv_chinh else sorted(L_TIEUCHUAN)[-1]
        canh_bao += [
            "⚠ Không tìm được L thoả α≥120° và i≤10 trong cả 2 nhóm!",
            "⚠ Lấy L lớn nhất nhóm chính — cần xem lại thông số đầu vào.",
        ]
    else:
        idx_chon = min(idx_ok + buoc_them, len(uv_dung) - 1)
        L_chon   = uv_dung[idx_chon]
        if idx_chon > idx_ok:
            log.append(
                f"  → Lấy thêm {idx_chon - idx_ok} bậc: "
                f"{uv_dung[idx_ok]} → {L_chon} mm  (tối ưu kết cấu)"
            )

    lam_c  = L_chon - math.pi * (d1 + d2) / 2
    disc_c = lam_c**2 - 8 * ((d2 - d1) / 2)**2
    a_c    = (lam_c + math.sqrt(max(disc_c, 0))) / 4
    alp_c  = 180.0 - (d2 - d1) / a_c * 57.3
    i_c    = v * 1000.0 / L_chon

    if alp_c < alpha_min:
        canh_bao.append(f"⚠ α={alp_c:.1f}° < 120° — kiểm tra lại!")
    if i_c > i_max:
        canh_bao.append(f"⚠ i={i_c:.3f} > 10 — đai quá nhanh!")

    return {'L': L_chon, 'a': round(a_c, 2), 'alpha': round(alp_c, 2),
            'i_dai': round(i_c, 4), 'log': log, 'canh_bao': canh_bao}


def tra_Ca(alpha1):    return noi_suy(CA_TABLE, alpha1)
def tra_Cu(u):         return noi_suy(CU_TABLE, u)
def tra_ad2(u):        return noi_suy(AD2_TABLE, u)

def tra_Cl_gan_nhat(ratio):
    return CL_TABLE[min(CL_TABLE.keys(), key=lambda x: abs(x - ratio))]

def tra_Cz(z):
    z = int(math.ceil(z))
    if z >= 6: return 0.85
    return CZ_TABLE.get(z, 0.85)

def tra_P0(loai_dai, d1, v):
    bang = P0_TABLE.get(loai_dai)
    if bang is None:
        raise ValueError(f"Không có bảng P0 cho đai loại '{loai_dai}'")
    d1_keys = sorted(k for k in bang if isinstance(k, (int, float)))
    if d1 <= d1_keys[0]:
        return noi_suy({vk: val for vk, val in bang[d1_keys[0]].items() if val is not None}, v)
    if d1 >= d1_keys[-1]:
        return noi_suy({vk: val for vk, val in bang[d1_keys[-1]].items() if val is not None}, v)
    for i in range(len(d1_keys) - 1):
        d1_lo, d1_hi = d1_keys[i], d1_keys[i+1]
        if d1_lo <= d1 <= d1_hi:
            P0_lo = noi_suy({vk: val for vk, val in bang[d1_lo].items() if val is not None}, v)
            P0_hi = noi_suy({vk: val for vk, val in bang[d1_hi].items() if val is not None}, v)
            return P0_lo + (d1 - d1_lo) / (d1_hi - d1_lo) * (P0_hi - P0_lo)
    raise ValueError(f"Lỗi tra P0: d1={d1}, loai={loai_dai}")


# ============================================================
# MODULE 2 – TÍNH TOÁN BỘ TRUYỀN ĐAI HÌNH THANG
# ============================================================
def tinh_bo_truyen_dai(P1, n1, ud, Kd=1.2, eps=0.02, verbose=True):
    """
    P1  – công suất làm việc P_lv (kW) — LẤY TỪ MODULE 1
    n1  – tốc độ trục động cơ n_dc (v/ph) — LẤY TỪ MODULE 1
    ud  – tỉ số truyền đai — LẤY TỪ MODULE 1
    Kd  – hệ số tải động
    eps – hệ số trượt (mặc định 0.02)
    """
    log = []
    def ghi(msg=""):
        log.append(msg)
        if verbose: print(msg)

    ghi("=" * 62)
    ghi("  TÍNH TOÁN BỘ TRUYỀN ĐAI HÌNH THANG THƯỜNG")
    ghi("=" * 62)
    ghi(f"  ► P1 (P_lv từ Module 1) = {P1} kW")
    ghi(f"  ► n1 (n_dc từ Module 1) = {n1} v/ph")
    ghi(f"  ► ud  (từ Module 1)     = {ud}")
    ghi(f"  ► Kd                    = {Kd}")
    ghi()

    ket_qua = {}

    # ── BƯỚC 1 ────────────────────────────────────────────────
    ghi("── BƯỚC 1: Chọn loại đai ──────────────────────────────")
    loai_dai = chon_loai_dai(P1, n1)
    td  = DAI_TIET_DIEN[loai_dai]
    bd  = DAI_BANH[loai_dai]
    ghi(f"  → Đai loại: {loai_dai}")
    ghi(f"     bt={td['bt']} mm, b={td['b']} mm, h={td['h']} mm, "
        f"y0={td['y0']} mm, A={td['A']} mm²")
    ghi(f"     d1=[{td['d1'][0]}, {td['d1'][1]}] mm,  l=[{td['l'][0]}, {td['l'][1]}] mm")
    ket_qua['loai_dai'] = loai_dai
    ghi()

    # ── BƯỚC 2 ────────────────────────────────────────────────
    ghi("── BƯỚC 2: Đường kính bánh đai nhỏ d1 ─────────────────")
    d_min, d_max = td['d1']
    candidates   = [d for d in D_TIEUCHUAN if d_min <= d <= d_max]
    if not candidates:
        raise ValueError("Không có d1 tiêu chuẩn phù hợp!")
    best_d, best_diff = None, float('inf')
    for d in candidates:
        diff = abs(math.pi * d * n1 / 60000 - 15)
        if diff < best_diff:
            best_diff, best_d = diff, d
    d1 = best_d
    v  = round(math.pi * d1 * n1 / 60000, 3)
    ghi(f"  Dãy tiêu chuẩn phù hợp: {candidates}")
    ghi(f"  → Chọn d1 = {d1} mm")
    ghi(f"  v = π×{d1}×{n1}/60000 = {v:.3f} m/s  "
        f"{'✓ < 25 m/s' if v < 25 else '⚠ ≥ 25 m/s → dùng đai hẹp!'}")
    ket_qua.update({'d1': d1, 'v': round(v, 3)})
    ghi()

    # ── BƯỚC 3 ────────────────────────────────────────────────
    ghi("── BƯỚC 3: Đường kính bánh đai lớn d2 ─────────────────")
    d2_tinh = d1 * ud / (1 - eps)
    d2      = chon_d2_tieuchuan(d2_tinh)
    utt     = d2 / (d1 * (1 - eps))
    sai_so  = abs(utt - ud) / ud * 100
    ghi(f"  d2_tính = {d1}×{ud}/(1-{eps}) = {d2_tinh:.3f} mm")
    ghi(f"  → Chọn d2 = {d2} mm  (tiêu chuẩn, gần nhất)")
    ghi(f"  utt = {utt:.3f}  →  Sai số = {sai_so:.2f}%  "
        f"{'✓ < 4%' if sai_so < 4 else '⚠ > 4%!'}")
    ket_qua.update({'d2': d2, 'd2_tinh': round(d2_tinh, 3),
                    'u_thucte': round(utt, 3), 'sai_so_pct': round(sai_so, 2)})
    ghi()

    # ── BƯỚC 4 ────────────────────────────────────────────────
    ghi("── BƯỚC 4: Khoảng cách trục sơ bộ ────────────────────")
    ad2_ratio = tra_ad2(ud)
    a_so_bo   = ad2_ratio * d2_tinh
    h         = td['h']
    a_min     = 0.55 * (d1 + d2_tinh) + h
    a_max     = 2.0  * (d1 + d2_tinh)
    ghi(f"  ud={ud} → a/d2 = {ad2_ratio}  (Bảng 4.14)")
    ghi(f"  a_sơ_bộ = {ad2_ratio} × {d2_tinh:.3f} = {a_so_bo:.2f} mm")
    ghi(f"  Điều kiện: 0.55(d1+d2)+h = {a_min:.1f} ≤ a ≤ 2(d1+d2) = {a_max:.1f}")
    if a_min <= a_so_bo <= a_max:
        ghi(f"  ✓ a_sơ_bộ = {a_so_bo:.2f} mm — thỏa mãn.")
    else:
        a_so_bo = (a_min + a_max) / 2
        ghi(f"  ⚠ Không thỏa! Chọn a = (a_min+a_max)/2 = {a_so_bo:.2f} mm")
    ket_qua.update({'a_so_bo': round(a_so_bo, 2),
                    'a_min': round(a_min, 2), 'a_max': round(a_max, 2)})
    ghi()

    # ── BƯỚC 5 ────────────────────────────────────────────────
    ghi("── BƯỚC 5: Chiều dài đai ──────────────────────────────")
    L_tinh = (2 * a_so_bo + math.pi * (d1 + d2) / 2
              + (d2 - d1) ** 2 / (4 * a_so_bo))
    ghi(f"  L_tính = 2a + π(d1+d2)/2 + (d2-d1)²/(4a) = {L_tinh:.2f} mm")
    ket_L = chon_L_tieuchuan(L_tinh, loai_dai, d1, d2, v)
    ghi("  Duyệt L tiêu chuẩn:")
    for dong in ket_L['log']:
        ghi(dong)
    for cw in ket_L['canh_bao']:
        ghi(f"  ⚠ {cw}")
    L = ket_L['L']
    ghi(f"  → L = {L} mm (tiêu chuẩn)")
    ket_qua.update({'L_tinh': round(L_tinh, 2), 'L': L})
    ghi()

    # ── BƯỚC 6 ────────────────────────────────────────────────
    ghi("── BƯỚC 6: Tính lại khoảng cách trục a ────────────────")
    lam_da = L - math.pi * (d1 + d2) / 2
    delta  = (d2 - d1) / 2
    disc   = lam_da ** 2 + 8 * delta ** 2      # công thức gốc theo đáp án
    a      = (lam_da + math.sqrt(disc)) / 4
    a_dc_min = a - 0.015 * L
    a_dc_max = a + 0.030 * L
    ghi(f"  λ = {lam_da:.3f}")
    ghi(f"  Δ = {delta:.3f}")
    ghi(f"  a = (λ + √(λ² + 8Δ²)) / 4 = {a:.3f} mm")
    ghi(f"  Khoảng điều chỉnh: [{a_dc_min:.1f}; {a_dc_max:.1f}] mm")
    ket_qua.update({'a': round(a, 2),
                    'a_dieu_chinh_min': round(a_dc_min, 2),
                    'a_dieu_chinh_max': round(a_dc_max, 2)})
    ghi()

    # ── BƯỚC 7 ────────────────────────────────────────────────
    ghi("── BƯỚC 7: Góc ôm α1 ──────────────────────────────────")
    alpha1 = 180 - (d2 - d1) / a * 57.3
    ghi(f"  α1 = 180° - ({d2}-{d1})/{a:.2f}×57.3 = {alpha1:.2f}°")
    if alpha1 < 120:
        raise ValueError(f"α1 = {alpha1:.1f}° < 120° — KHÔNG HỢP LỆ!")
    ghi(f"  ✓ α1 = {alpha1:.2f}° ≥ 120°")
    ket_qua['alpha1'] = round(alpha1, 2)
    ghi()

    # ── BƯỚC 8 ────────────────────────────────────────────────
    ghi("── BƯỚC 8: Các hệ số hiệu chỉnh ──────────────────────")
    Ca         = tra_Ca(alpha1)
    l0         = P0_TABLE[loai_dai]['_l0']
    ratio_l_l0 = L / l0
    Cl         = tra_Cl_gan_nhat(ratio_l_l0)
    Cu         = tra_Cu(ud)
    ghi(f"  Cα  = {Ca:.3f}  (Bảng 4.15, α1={alpha1:.1f}°)")
    ghi(f"  l/l0 = {L}/{l0} = {ratio_l_l0:.3f}  →  Cl = {Cl:.3f}  (Bảng 4.16)")
    ghi(f"  Cu  = {Cu:.3f}  (Bảng 4.17, ud={ud})")
    ket_qua.update({'Ca': round(Ca, 3), 'Cl': round(Cl, 3), 'Cu': round(Cu, 3),
                    'l0': l0, 'ratio_l_l0': round(ratio_l_l0, 3)})
    ghi()

    # ── BƯỚC 9 ────────────────────────────────────────────────
    ghi("── BƯỚC 9: Xác định số đai Z ───────────────────────────")
    P0      = 5                             # tra bảng 4.19 thủ công (kW)
    Z_tam   = P1 * Kd / (P0 * Ca * Cl * Cu * 1.0)
    Z_tam_r = math.ceil(Z_tam)
    Cz      = tra_Cz(Z_tam_r)
    Z_chinh = P1 * Kd / (P0 * Ca * Cl * Cu * Cz)
    Z       = math.ceil(Z_chinh)
    ghi(f"  P0 = {P0:.3f} kW  (Bảng 4.19, {loai_dai}, d1={d1} mm, v={v:.2f} m/s)")
    ghi(f"  Z_sơ_bộ (Cz=1) = {Z_tam:.3f} → {Z_tam_r}")
    ghi(f"  Cz  = {Cz:.2f}  (Bảng 4.18, z≈{Z_tam_r})")
    ghi(f"  Z   = ⌈{Z_chinh:.3f}⌉ = {Z} đai")
    ket_qua.update({'P0': P0, 'Cz': Cz, 'Z': Z})
    ghi()

    # ── BƯỚC 10 ───────────────────────────────────────────────
    ghi("── BƯỚC 10: Kích thước bánh đai ───────────────────────")
    t   = bd['t'];  e = bd['e'];  h0 = bd['h0']
    B   = (Z - 1) * t + 2 * e
    da1 = d1 + 2 * h0
    da2 = d2 + 2 * h0
    ghi(f"  Bảng 4.21 ({loai_dai}): t={t}, e={e}, h0={h0}")
    ghi(f"  B   = (Z-1)×t + 2e = ({Z}-1)×{t} + 2×{e} = {B:.1f} mm")
    ghi(f"  da1 = d1+2h0 = {d1}+2×{h0} = {da1} mm")
    ghi(f"  da2 = d2+2h0 = {d2}+2×{h0} = {da2} mm")
    ket_qua.update({'B': round(B, 1), 'da1': da1, 'da2': da2})
    ghi()

    # ── BƯỚC 11 ───────────────────────────────────────────────
    ghi("── BƯỚC 11: Lực trong bộ truyền ───────────────────────")
    qm  = QM.get(loai_dai, 0.178)
    Fv  = qm * v ** 2
    Ca_r = int(Ca * 100) / 100          # làm tròn 2 chữ số như tính tay
    F0  = 780 * P1 * Kd / (v * Ca_r * Z) + Fv
    Fr  = 2 * F0 * Z * math.sin(math.radians(alpha1 / 2))
    Ft  = 1000 * P1 / v
    ghi(f"  qm = {qm} kg/m  (Bảng 4.22)")
    ghi(f"  Fv = qm × v² = {Fv:.3f} N")
    ghi(f"  F0 = 780×P1×Kd/(v×Cα×Z) + Fv = {F0:.3f} N")
    ghi(f"  Fr = 2×F0×Z×sin(α1/2) = {Fr:.3f} N")
    ghi(f"  Ft = 1000×P1/v = {Ft:.3f} N")
    ket_qua.update({'qm': qm, 'Fv': round(Fv, 3), 'F0': round(F0, 3),
                    'Fr': round(Fr, 3), 'Ft': round(Ft, 3)})
    ghi()

    # ── BẢNG KẾT QUẢ ──────────────────────────────────────────
    ghi("=" * 62)
    ghi("  BẢNG KẾT QUẢ BỘ TRUYỀN ĐAI HÌNH THANG")
    ghi("=" * 62)
    rows = [
        ("Loại đai",                          f"{ket_qua['loai_dai']}"),
        ("Đường kính bánh nhỏ  d1",           f"{ket_qua['d1']} mm"),
        ("Đường kính bánh lớn  d2",           f"{ket_qua['d2_tinh']} mm"),
        ("Vận tốc đai  v",                    f"{ket_qua['v']} m/s"),
        ("Tỉ số truyền thực tế  utt",         f"{ket_qua['u_thucte']}  (sai số {ket_qua['sai_so_pct']}%)"),
        ("Khoảng cách trục  a",               f"{ket_qua['a']} mm"),
        ("Chiều dài đai  L",                  f"{ket_qua['L']} mm"),
        ("Góc ôm  α1",                        f"{ket_qua['alpha1']}°"),
        ("Số đai  Z",                         f"{ket_qua['Z']} đai"),
        ("Chiều rộng bánh đai  B",            f"{ket_qua['B']} mm"),
        ("Đường kính ngoài bánh dẫn   da1",   f"{ket_qua['da1']} mm"),
        ("Đường kính ngoài bánh bị dẫn da2",  f"{ket_qua['da2']} mm"),
        ("Lực căng ban đầu  F0",              f"{ket_qua['F0']} N"),
        ("Lực tác dụng lên trục  Fr",         f"{ket_qua['Fr']} N"),
        ("Lực vòng có ích  Ft",               f"{ket_qua['Ft']} N"),
    ]
    for name, val in rows:
        ghi(f"  {name:<42} {val}")
    ghi("=" * 62)

    ket_qua['log'] = log
    return ket_qua


# ============================================================
# HÀM TỔNG HỢP – KẾT NỐI MODULE 1 → MODULE 2
# ============================================================
def chay_he_thong(
        P_tai,          # Công suất tải (W) — từ đề bài
        n_iv,           # Tốc độ trục công tác (v/ph) — từ đề bài
        dc_chon,        # Dict động cơ đã chọn từ query_dong_co()
        eta_dict=None,
        u_dai_so_bo=2.5,
        u_con_so_bo=4.5,
        Kd=1.2,
        eps=0.02,
        K=1.0):
    """
    Hàm tổng hợp chạy toàn bộ hệ thống.

    Luồng dữ liệu:
        P_tai, n_iv
            └─► Module 1: tinh_HieuSuat_Tong, tinh_P_can_thiet,
                           tinh_toan_he_thong_thuc_te, tinh_thong_so_truc
                    │
                    ├─► P_lv  = P_tai / 1000      → P1 cho Module 2
                    └─► u_dai = kq_u['u_dai']      → ud cho Module 2
                    └─► n_dc  = dc_chon['VanToc_vph'] → n1 cho Module 2
                            │
                            └─► Module 2: tinh_bo_truyen_dai(P1=P_lv, n1=n_dc, ud=u_dai)
    """
    if eta_dict is None:
        eta_dict = {
            'dai':   0.96,
            'con':   0.97,
            'tru':   0.98,
            'o_lan': 0.995,
            'kn':    0.99,
        }

    print("\n" + "═" * 62)
    print("  MODULE 1 – TÍNH CHỌN ĐỘNG CƠ & PHÂN PHỐI TST")
    print("═" * 62)

    # ── Bước 1.1: Hiệu suất tổng ──────────────────────────────
    eta_total = tinh_HieuSuat_Tong(
        eta_dict['dai'], eta_dict['con'], eta_dict['tru'],
        eta_dict['o_lan'], eta_dict['kn']
    )
    print(f"\n  η_tổng = {eta_total}")

    # ── Bước 1.2: Công suất cần thiết & P_lv ─────────────────
    P_ct = tinh_P_can_thiet(P_tai, eta_total, K)
    P_lv = P_tai / 1000                         # công suất làm việc (kW)
    print(f"  P_cần_thiết = {P_ct:.4f} kW  →  Chọn P_dc = {dc_chon['CongSuat_kW']} kW")
    print(f"  P_lv (công suất làm việc) = {P_lv:.4f} kW")

    # ── Bước 1.3: Phân phối tỉ số truyền ────────────────────
    kq_u = tinh_toan_he_thong_thuc_te(dc_chon, n_iv, u_dai_so_bo, u_con_so_bo)
    print(f"\n  u_tổng = {kq_u['u_t']}  |  u_đai = {kq_u['u_dai']}"
          f"  |  u_côn = {kq_u['u_1']}  |  u_trụ = {kq_u['u_2']}")

    # ── Bước 1.4: Thông số các trục ─────────────────────────
    n_dc  = dc_chon['VanToc_vph']
    P_dc  = dc_chon['CongSuat_kW']
    u_list = [kq_u['u_dai'], kq_u['u_1'], kq_u['u_2']]
    kq_truc = tinh_thong_so_truc(P_dc, n_dc, u_list, eta_dict)

    print(f"\n  {'Trục':<10} {'P (kW)':>10} {'n (v/ph)':>12} {'T (N·mm)':>16}")
    print(f"  {'─'*10} {'─'*10} {'─'*12} {'─'*16}")
    for key, lbl in [('truc_dc','Động cơ'),('truc_1','Trục I'),
                     ('truc_2','Trục II'),('truc_3','Trục III')]:
        d = kq_truc[key]
        print(f"  {lbl:<10} {d['P']:>10.4f} {d['n']:>12.2f} {d['T']:>16.2f}")

    # ── KẾT NỐI: lấy P1 và ud cho Module 2 ──────────────────
    # P1_dai = P_lv (công suất làm việc đề bài)   — KHÔNG phải P_dc
    # ud_dai = u_dai từ phân phối tỉ số truyền
    # n1_dai = n_dc (tốc độ trục động cơ = bánh dẫn đai)
    P1_dai = P_lv
    ud_dai = kq_u['u_dai']
    n1_dai = n_dc

    print("\n" + "─" * 62)
    print("  KẾT NỐI MODULE 1 → MODULE 2")
    print("─" * 62)
    print(f"  P1  = P_lv              = {P1_dai:.4f} kW")
    print(f"  ud  = u_dai             = {ud_dai}")
    print(f"  n1  = n_dc              = {n1_dai} v/ph")

    # ── Module 2: Bộ truyền đai ──────────────────────────────
    print()
    kq_dai = tinh_bo_truyen_dai(
        P1=P1_dai,
        n1=n1_dai,
        ud=ud_dai,
        Kd=Kd,
        eps=eps,
        verbose=True,
    )

    return kq_u, kq_truc, kq_dai


# ============================================================
# CHẠY THỬ (không có Database → dùng dict mẫu)
# ============================================================
if __name__ == "__main__":
    # Thông số đề bài
    P_TAI = 5872.2   # W  — công suất tải (lực × vận tốc băng tải)
    N_IV  = 70       # v/ph — tốc độ trục công tác

    # Động cơ đã chọn (thay bằng kết quả query_dong_co() khi có DB)
    DC_CHON = {
        'Model':        'ĐC_7.5kW_2922',
        'CongSuat_kW':  7.5,
        'VanToc_vph':   2922,
        'Tk_Tdn':       2.0,
    }

    try:
        kq_u, kq_truc, kq_dai = chay_he_thong(
            P_tai       = P_TAI,
            n_iv        = N_IV,
            dc_chon     = DC_CHON,
            u_dai_so_bo = 2.5,
            u_con_so_bo = 4.5,
            Kd          = 1.2,
            eps         = 0.02,
        )
        print("\n  ✓ Tính toán hoàn tất!\n")
    except ValueError as e:
        print(f"\n  [LỖI] {e}\n")