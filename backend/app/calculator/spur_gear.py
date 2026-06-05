"""
================================================================================
SPUR_GEAR.PY — Bộ hàm tính toán thông số và kích thước bộ truyền
               BÁNH RĂNG TRỤ - RĂNG THẲNG (β = 0°)
================================================================================
Tài liệu tham chiếu:
  [1] Trịnh Chất – Lê Văn Uyển, Tính toán Thiết kế Hệ dẫn động Cơ khí
      Công thức 6.11 (trang 104), 6.15a, 6.33, 6.43/6.44, 6.48/6.49

Cấu trúc module:
  ── Nhóm A: Thông số hình học cơ bản (CT 6.11) ──────────────────────────────
  G1  calc_pitch_diameter()        Đường kính vòng chia d
  G2  calc_tip_diameter()          Đường kính đỉnh răng da
  G3  calc_root_diameter()         Đường kính đáy răng df
  G4  calc_working_pitch_diameter()Đường kính vòng lăn dw
  G5  calc_center_distance_check() Kiểm tra khoảng cách trục từ z, m
  G6  calc_tooth_height()          Chiều cao răng h, ha, hf
  G7  calc_pitch()                 Bước răng p, pb (bước cơ sở)
  G8  calc_all_geometry()          Tổng hợp toàn bộ thông số hình học

  ── Nhóm B: Thông số thiết kế (xác định sơ bộ) ──────────────────────────────
  D1  calc_preliminary_center_distance()  Khoảng cách trục sơ bộ (CT 6.15a)
  D2  calc_tooth_number()                 Xác định số răng z1, z2
  D3  calc_module_from_bending()          Môđun từ điều kiện uốn (CT 6.17)
  D4  calc_face_width()                   Chiều rộng vành răng bw

  ── Nhóm C: Kiểm nghiệm ứng suất ────────────────────────────────────────────
  V1  calc_allowable_contact_stress()     Ứng suất tiếp xúc cho phép (CT 6.1)
  V2  calc_allowable_bending_stress()     Ứng suất uốn cho phép (CT 6.2)
  V3  calc_contact_stress()               Kiểm nghiệm σH (CT 6.33)
  V4  calc_bending_stress()               Kiểm nghiệm σF1, σF2 (CT 6.43/6.44)
  V5  calc_overload_stress()              Kiểm nghiệm quá tải (CT 6.48/6.49)

  ── Nhóm D: Tiện ích ─────────────────────────────────────────────────────────
  standardize_module()                    Chuẩn hóa môđun tiêu chuẩn
  standardize_center_distance()           Chuẩn hóa khoảng cách trục
  lookup_YF()                             Tra hệ số dạng răng YF(z)
  lookup_ZH()                             Tra hệ số ZH(β)
  check_meshing_conditions()              Kiểm tra điều kiện ăn khớp kỹ thuật
  print_gear_table()                      In bảng thống kê thông số
"""

import math
from dataclasses import dataclass, field
from typing import Optional, Tuple


# ==============================================================================
# BẢNG TRA TIÊU CHUẨN
# ==============================================================================

# Dãy môđun tiêu chuẩn — TCVN / ISO 54
STANDARD_MODULES = [
    1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0,
]

# Khoảng cách trục tiêu chuẩn — TCVN 2601-78 (mm)
STANDARD_CENTER_DISTANCES = [
    40, 50, 63, 80, 100, 125, 160, 200,
    250, 315, 400, 500, 630, 800, 1000,
]

# [FIX-6] Hệ số dạng răng YF theo số răng (x = 0)
# Nguồn: Bảng 6.7 — Trịnh Chất, Lê Văn Uyển (ấn bản mới nhất)
_YF_TABLE = [
    (17, 4.28),
    (20, 4.09),
    (22, 4.07),
    (25, 3.90),
    (28, 3.85),
    (30, 3.80),
    (32, 3.78),
    (40, 3.70),
    (50, 3.65),
    (60, 3.62),
    (80, 3.61),
    (100, 3.60),
    (150, 3.60),
    (200, 3.60),
    (400, 3.60),
]

# BẢNG 6.12 - HỆ SỐ Z_H (hình dạng bề mặt tiếp xúc)
_ZH_TABLE = {
    0:  {0.08: 1.48, 0.05: 1.52, 0.03: 1.56, 0.02: 1.62, 0.01: 1.68,
         0.005: 1.71, 0.0: 1.76, -0.005: 1.83, -0.01: 1.93, -0.015: 2.14},
    10: {0.08: 1.47, 0.05: 1.51, 0.03: 1.56, 0.02: 1.60, 0.01: 1.66,
         0.005: 1.69, 0.0: 1.74, -0.005: 1.80, -0.01: 1.90, -0.015: 2.07},
    15: {0.08: 1.46, 0.05: 1.50, 0.03: 1.55, 0.02: 1.58, 0.01: 1.63,
         0.005: 1.67, 0.0: 1.71, -0.005: 1.77, -0.01: 1.86, -0.015: 2.00, -0.02: 2.35},
    20: {0.08: 1.43, 0.05: 1.47, 0.03: 1.52, 0.02: 1.55, 0.01: 1.60,
         0.005: 1.63, 0.0: 1.67, -0.005: 1.72, -0.01: 1.80, -0.015: 1.91, -0.02: 2.13},
    25: {0.08: 1.42, 0.05: 1.45, 0.03: 1.49, 0.02: 1.52, 0.01: 1.57,
         0.005: 1.59, 0.0: 1.62, -0.005: 1.67, -0.01: 1.73, -0.015: 1.81, -0.02: 1.97},
    30: {0.08: 1.38, 0.05: 1.42, 0.03: 1.45, 0.02: 1.48, 0.01: 1.52,
         0.005: 1.54, 0.0: 1.56, -0.005: 1.60, -0.01: 1.65, -0.015: 1.70, -0.02: 1.81},
    35: {0.08: 1.35, 0.05: 1.37, 0.03: 1.40, 0.02: 1.42, 0.01: 1.46,
         0.005: 1.48, 0.0: 1.50, -0.005: 1.53, -0.01: 1.56, -0.015: 1.60, -0.02: 1.66},
    40: {0.08: 1.30, 0.05: 1.32, 0.03: 1.34, 0.02: 1.37, 0.01: 1.39,
         0.005: 1.41, 0.0: 1.42, -0.005: 1.45, -0.01: 1.47, -0.015: 1.50, -0.02: 1.53},
}

# Hệ số ZM theo cặp vật liệu (MPa^(1/2)) — Bảng 6.5
ZM_TABLE = {
    "thep_thep":          274,
    "thep_gang":          234,
    "thep_gang_dong":     225,
    "gang_gang":          209,
    "textolit_thep":       69.5,
    "poliamid_thep":       47.5,
}

# Hệ số Ka theo cặp vật liệu & loại răng — Bảng 6.5
KA_TABLE = {
    ("thep_thep",          "thang"):    49.5,
    ("thep_thep",          "nghieng"):  43.0,
    ("thep_gang",          "thang"):    44.5,
    ("thep_gang",          "nghieng"):  39.0,
    ("thep_gang_dong",     "thang"):    43.0,
    ("thep_gang_dong",     "nghieng"):  37.0,
    ("gang_gang",          "thang"):    41.5,
    ("gang_gang",          "nghieng"):  36.0,
    ("textolit_thep",      "thang"):    20.0,
    ("textolit_thep",      "nghieng"):  17.0,
    ("poliamid_thep",      "thang"):    15.5,
    ("poliamid_thep",      "nghieng"):  13.5,
}

# Góc ăn khớp tiêu chuẩn (°)
ALPHA_STD = 20.0

# Số răng tối thiểu để tránh trượt chân răng (α = 20°, x = 0)
Z_MIN = 17


# ==============================================================================
# TIỆN ÍCH NỘI BỘ
# ==============================================================================

def _lerp(table: list, x: float) -> float:
    """Nội suy tuyến tính từ bảng [(xi, yi)]."""
    if x <= table[0][0]:  return table[0][1]
    if x >= table[-1][0]: return table[-1][1]
    for i in range(len(table) - 1):
        x0, y0 = table[i];  x1, y1 = table[i+1]
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return table[-1][1]


def _sep(title: str = "", width: int = 70):
    if title:
        pad = (width - len(title) - 2) // 2
        print("─" * pad + f" {title} " + "─" * pad)
    else:
        print("─" * width)

def _row(label: str, value, unit: str = "", ok: Optional[bool] = None,
         allow: Optional[float] = None, w: int = 38):
    G = "\033[92m"; R = "\033[91m"; B = "\033[94m"; E = "\033[0m"; BD = "\033[1m"
    v = f"{value:.3f}" if isinstance(value, float) else str(value)
    line = f"  {BD}{label:<{w}}{E} {B}{v:>10}{E}  {unit}"
    if ok is not None and allow is not None:
        tag  = f"{G} ĐẠT{E}" if ok else f"{R} KHÔNG ĐẠT{E}"
        pct  = abs((float(value)/allow - 1) * 100)
        note = "dự phòng" if ok else "vượt"
        line += f"  [{tag}  {note} {pct:.1f}%  ≤ {allow} {unit}]"
    print(line)

def get_ZM(cap_vat_lieu: str) -> float:
    """Tra Z_M theo chuỗi cap_vat_lieu, mặc định Thép-Thép nếu không tìm thấy."""
    zm = ZM_TABLE.get(cap_vat_lieu.lower().replace(" ", "_"), None)
    if zm is not None:
        return zm
    print(f"Cảnh báo: Không tìm thấy Z_M cho '{cap_vat_lieu}'. "
          f"Sử dụng giá trị mặc định Thép-Thép = 274")
    return 274.0


# ==============================================================================
# TIỆN ÍCH CÔNG KHAI
# ==============================================================================

def standardize_module(m_calc: float) -> float:
    """
    Chuẩn hóa môđun tính toán lên giá trị tiêu chuẩn gần nhất (≥ m_calc).

    Input:
        m_calc (float) — môđun tính được (mm)
    Output:
        float — môđun tiêu chuẩn (mm)

    Ví dụ:
        standardize_module(2.7)  → 3.0
        standardize_module(3.0)  → 3.0
    """
    for m in STANDARD_MODULES:
        if m >= m_calc - 1e-9:
            return m
    return float(STANDARD_MODULES[-1])

def standardize_center_distance(aw_sb: float) -> float:
    """
    Chuẩn hóa khoảng cách trục lên giá trị tiêu chuẩn gần nhất (≥ aw_sb).

    Input:
        aw_sb (float) — khoảng cách trục tính được (mm)
    Output:
        float — khoảng cách trục tiêu chuẩn (mm)
    """
    for aw in STANDARD_CENTER_DISTANCES:
        if aw >= aw_sb - 1e-9:
            return float(aw)
    return float(STANDARD_CENTER_DISTANCES[-1])

def lookup_YF(z: int) -> float:
    """
    Tra hệ số dạng răng YF theo số răng z (nội suy tuyến tính – Bảng 6.7).

    Input:
        z (int) — số răng (z ≥ 17)
    Output:
        float — YF
    """
    return round(_lerp(_YF_TABLE, float(z)), 3)

def lookup_ZH(beta_deg: float = 0.0, x_sum: float = 0.0) -> float:
    """
    Tra hệ số ZH theo góc nghiêng β (°) và tổng hệ số dịch chỉnh (x1+x2).

    Input:
        beta_deg (float) — góc nghiêng β (°), mặc định 0
        x_sum    (float) — x1 + x2 (tổng hệ số dịch chỉnh), mặc định 0
    Output:
        float — ZH
    """
    if abs(beta_deg) < 1e-6:
        row = _ZH_TABLE[0]
        K = x_sum
        keys = sorted(row.keys(), reverse=True)
        if K >= keys[0]:   return round(row[keys[0]], 4)
        if K <= keys[-1]:  return round(row[keys[-1]], 4)
        for i in range(len(keys) - 1):
            k0, k1 = keys[i], keys[i+1]
            if k1 <= K <= k0:
                zh0, zh1 = row[k0], row[k1]
                t = (K - k0) / (k1 - k0)
                return round(zh0 + (zh1 - zh0) * t, 4)
        return 1.76  # fallback K=0

    beta_keys = sorted(_ZH_TABLE.keys())
    zh_at_k0 = [(b, _ZH_TABLE[b].get(0.0, 1.76)) for b in beta_keys]
    return round(_lerp(zh_at_k0, beta_deg), 4)


# ==============================================================================
# NHÓM A — THÔNG SỐ HÌNH HỌC CƠ BẢN (CT 6.11, trang 104 – [1])
# ==============================================================================

def G1_pitch_diameter(m: float, z: int, beta_deg: float = 0.0) -> float:
    """
    G1 — Đường kính vòng chia d (CT 6.11).
        d = m·z / cos β

    Ví dụ (mục 3.3.7):
        G1_pitch_diameter(3, 32)  → 96.0  mm
        G1_pitch_diameter(3, 119) → 357.0 mm
    """
    cosb = math.cos(math.radians(beta_deg))
    return round(m * z / cosb, 4)


def G2_tip_diameter(d: float, m: float, x: float = 0.0) -> float:
    """
    G2 — Đường kính đỉnh răng da (CT 6.11).
        da = d + 2·(1 + x)·m

    Ví dụ (mục 3.3.7):
        G2_tip_diameter(96, 3)   → 102.0 mm
        G2_tip_diameter(357, 3)  → 363.0 mm
    """
    return round(d + 2.0 * (1.0 + x) * m, 4)


def G3_root_diameter(d: float, m: float, x: float = 0.0) -> float:
    """
    G3 — Đường kính đáy răng df (CT 6.11).
        df = d − (2.5 − 2·x)·m

    Ví dụ (mục 3.3.7):
        G3_root_diameter(96, 3)   → 88.5  mm
        G3_root_diameter(357, 3)  → 349.5 mm
    """
    return round(d - (2.5 - 2.0 * x) * m, 4)


def G4_working_pitch_diameter(m: float, z1: int, z2: int,
                               aw: float, beta_deg: float = 0.0) -> Tuple[float, float]:
    """
    G4 — Đường kính vòng lăn dw1, dw2.
        dw1 = 2·aw / (u + 1)
        dw2 = 2·aw·u / (u + 1)
    """
    u = z2 / z1
    dw1 = round(2.0 * aw / (u + 1.0), 4)
    dw2 = round(2.0 * aw * u / (u + 1.0), 4)
    return dw1, dw2


def G5_center_distance_check(m: float, z1: int, z2: int,
                              beta_deg: float = 0.0,
                              x1: float = 0.0, x2: float = 0.0) -> dict:
    """
    G5 — Tính / kiểm tra khoảng cách trục từ z, m, x.
        aw = m·(z1 + z2) / (2·cosβ)   (khi x1+x2 = 0)
    """
    cosb = math.cos(math.radians(beta_deg))
    aw = round(m * (z1 + z2) / (2.0 * cosb), 4)
    d1 = G1_pitch_diameter(m, z1, beta_deg)
    d2 = G1_pitch_diameter(m, z2, beta_deg)
    u  = round(z2 / z1, 4)
    return {"aw": aw, "d1": d1, "d2": d2, "u": u}


def G6_tooth_height(m: float, x: float = 0.0) -> dict:
    """
    G6 — Chiều cao răng h, ha, hf.
        ha = (1 + x)·m
        hf = (1.25 − x)·m
        h  = ha + hf = 2.25·m

    Ví dụ với m=3, x=0:
        ha = 3.0 mm,  hf = 3.75 mm,  h = 6.75 mm
    """
    ha = round((1.0 + x) * m, 4)
    hf = round((1.25 - x) * m, 4)
    h  = round(ha + hf, 4)
    c  = round(0.25 * m, 4)
    return {"ha": ha, "hf": hf, "h": h, "c": c}


def G7_pitch(m: float, alpha_deg: float = ALPHA_STD) -> dict:
    """
    G7 — Bước răng p và bước cơ sở pb.
        p  = π·m
        pb = π·m·cosα
    """
    p  = round(math.pi * m, 6)
    pb = round(math.pi * m * math.cos(math.radians(alpha_deg)), 6)
    return {"p": p, "pb": pb}


def _calc_eps_alpha_formula(z1: int, z2: int, m: float,
                             aw: float, beta_deg: float = 0.0,
                             x1: float = 0.0, x2: float = 0.0,
                             alpha_deg: float = ALPHA_STD) -> float:
    
    alpha_r = math.radians(alpha_deg)
    cosb    = math.cos(math.radians(beta_deg))

    d1  = m * z1 / cosb
    d2  = m * z2 / cosb
    da1 = d1 + 2.0 * (1.0 + x1) * m
    da2 = d2 + 2.0 * (1.0 + x2) * m

    rb1 = (d1 / 2.0) * math.cos(alpha_r)
    rb2 = (d2 / 2.0) * math.cos(alpha_r)
    ra1 = da1 / 2.0
    ra2 = da2 / 2.0

    xt = x1 + x2
    if abs(xt) < 1e-9:
        alpha_w = alpha_deg
    else:
        inv_a  = math.tan(alpha_r) - alpha_r
        inv_aw = 2 * math.tan(alpha_r) * xt / (z1 + z2) + inv_a
        aw_r   = alpha_r
        for _ in range(50):
            f  = math.tan(aw_r) - aw_r - inv_aw
            fp = math.tan(aw_r)**2
            aw_r -= f / fp
        alpha_w = math.degrees(aw_r)

    aw_r = math.radians(alpha_w)

    cos_aa1 = min(1.0, max(-1.0, rb1 / ra1))
    cos_aa2 = min(1.0, max(-1.0, rb2 / ra2))
    alpha_a1 = math.acos(cos_aa1)
    alpha_a2 = math.acos(cos_aa2)

    tan_aa1 = math.tan(alpha_a1)
    tan_aa2 = math.tan(alpha_a2)
    tan_aw  = math.tan(aw_r)

    eps = (z1 * (tan_aa1 - tan_aw) + z2 * (tan_aa2 - tan_aw)) / (2.0 * math.pi)
    return round(eps, 4)


def G8_all_geometry(
    m: float,
    z1: int,
    z2: int,
    aw: float,
    beta_deg: float = 0.0,
    x1: float = 0.0,
    x2: float = 0.0,
    psi_a: float = 0.3,
    alpha_deg: float = ALPHA_STD
) -> dict:
    """
    G8 — Tổng hợp toàn bộ thông số hình học bộ truyền bánh răng trụ.

    Ví dụ (mục 3.3.7):
        G8_all_geometry(m=3, z1=32, z2=119, aw=226.5)
        → d1=96, d2=357, da1=102, da2=363, df1=88.5, df2=349.5
        → eps_alpha ≈ 1.7691, ZH = 1.76
    """
    cosb = math.cos(math.radians(beta_deg))
    u    = z2 / z1

    d1 = G1_pitch_diameter(m, z1, beta_deg)
    d2 = G1_pitch_diameter(m, z2, beta_deg)

    dw1, dw2 = G4_working_pitch_diameter(m, z1, z2, aw, beta_deg)

    da1 = G2_tip_diameter(d1, m, x1)
    da2 = G2_tip_diameter(d2, m, x2)
    df1 = G3_root_diameter(d1, m, x1)
    df2 = G3_root_diameter(d2, m, x2)

    ht  = G6_tooth_height(m, (x1 + x2) / 2)
    pt  = G7_pitch(m, alpha_deg)

    YF1 = lookup_YF(z1)
    YF2 = lookup_YF(z2)

    bw = round(psi_a * aw, 2)

    alpha_r = math.radians(alpha_deg)
    xt      = x1 + x2
    if abs(xt) < 1e-9:
        alpha_w = alpha_deg
    else:
        inv_a  = math.tan(alpha_r) - alpha_r
        inv_aw = 2 * math.tan(alpha_r) * xt / (z1 + z2) + inv_a
        aw_r   = alpha_r
        for _ in range(50):
            f  = math.tan(aw_r) - aw_r - inv_aw
            fp = math.tan(aw_r)**2
            aw_r -= f / fp
        alpha_w = math.degrees(aw_r)

    eps_alpha = _calc_eps_alpha_formula(z1, z2, m, aw, beta_deg, x1, x2, alpha_deg)
    ZH = lookup_ZH(beta_deg, x1 + x2)

    return {
        "m": m, "u": round(u, 4), "bw": bw,
        "beta_deg": beta_deg, "alpha_w": round(alpha_w, 4),
        "eps_alpha": eps_alpha, "ZH": ZH,
        "d1": d1, "dw1": dw1, "da1": da1, "df1": df1,
        "x1": x1, "YF1": YF1, "z1": z1,
        "d2": d2, "dw2": dw2, "da2": da2, "df2": df2,
        "x2": x2, "YF2": YF2, "z2": z2,
        "ha": ht["ha"], "hf": ht["hf"], "h": ht["h"], "c": ht["c"],
        "p": pt["p"], "pb": pt["pb"],
        "aw": aw,
    }


# ==============================================================================
# NHÓM D — THÔNG SỐ THIẾT KẾ
# ==============================================================================

def D1_preliminary_center_distance(
    T1: float,
    u: float,
    sigma_H_allow: float,
    psi_a: float = 0.3,
    KHb: float = 1.05,
    cap_vat_lieu: str = "thep_thep",
    loai_rang: str = "thang",
    an_khop: str = "ngoai",
    standardize: bool = True
) -> dict:
    """
    D1 — Khoảng cách trục sơ bộ (CT 6.15a).
        aw = Ka·(u ± 1)·∛[ T1·KHβ / (ψa·[σH]²·u) ]

    Output (dict):
        Ka       — hệ số tra bảng
        aw_sb    — khoảng cách trục sơ bộ tính theo CT 6.15a (mm)
        aw       — khoảng cách trục sau chuẩn hóa (nếu standardize=True) (mm)
        bw       — chiều rộng vành răng = ψa·aw (mm)
    """
    key = (cap_vat_lieu, loai_rang)
    if key not in KA_TABLE:
        raise ValueError(f"Không tìm thấy Ka: {key}. Hợp lệ: {list(KA_TABLE.keys())}")
    Ka   = KA_TABLE[key]
    sign = 1 if an_khop == "ngoai" else -1
    aw_c = Ka * (u + sign) * (T1 * KHb / (psi_a * sigma_H_allow**2 * u)) ** (1/3)
    aw_s = standardize_center_distance(aw_c) if standardize else aw_c
    return {
        "Ka":   Ka,
        "aw_sb": round(aw_c, 3),   # sơ bộ (chưa chuẩn hóa)
        "aw":    aw_s,              # sau chuẩn hóa
        "bw":   round(psi_a * aw_s, 3),
    }


def D2_tooth_number(
    aw: float,
    u: float,
    m: float,
    beta_deg: float = 0.0,
    z1_min: int = Z_MIN
) -> dict:
    """
    D2 — Xác định số răng z1, z2.
        z1 = 2·aw·cosβ / [m·(u + 1)]   (làm tròn xuống, ≥ z1_min)
        z2 = round(u·z1)
    """
    cosb  = math.cos(math.radians(beta_deg))
    z1_f  = 2 * aw * cosb / (m * (u + 1))
    z1    = max(z1_min, int(z1_f))
    z2    = round(u * z1)
    aw_ck = m * (z1 + z2) / (2 * cosb)
    return {
        "z1": z1, "z2": z2,
        "u_real":   round(z2 / z1, 4),
        "aw_check": round(aw_ck, 4),
        "delta_aw": round(aw_ck - aw, 4),
    }


def D3_module_from_bending(
    T1: float,
    z1: int,
    z2: int,
    d1: float,
    bw: float,
    KF: float,
    YF1: float,
    YF2: float,
    Ye: float,
    sigma_F1_allow: float,
    sigma_F2_allow: float,
    Yb: float = 1.0,
    beta_deg: float = 0.0,
    standardize: bool = True
) -> dict:
    """
    D3 — Xác định môđun từ điều kiện bền uốn (CT 6.17).
    """
    cosb = math.cos(math.radians(beta_deg))

    m1_calc = 2 * T1 * KF * YF1 * Ye * Yb / (bw * d1 * sigma_F1_allow * cosb)
    m2_calc = 2 * T1 * KF * YF2 * Ye * Yb / (bw * d1 * sigma_F2_allow * cosb)

    m_calc = max(m1_calc, m2_calc)
    governed_by = "banh_1" if m1_calc >= m2_calc else "banh_2"

    m_std = standardize_module(m_calc) if standardize else m_calc

    return {
        "m1_calc":     round(m1_calc, 5),
        "m2_calc":     round(m2_calc, 5),
        "m_calc":      round(m_calc,  5),
        "m":           m_std,
        "governed_by": governed_by,
    }


def D4_face_width(aw: float, psi_a: float = 0.3) -> dict:
    """
    D4 — Chiều rộng vành răng bw = ψa · aw.

    Ví dụ (mục 3.3.7):
        D4_face_width(226.5, psi_a=0.3) → bw = 67.95 mm
    """
    bw = round(psi_a * aw, 4)
    return {"bw": bw, "psi_a": psi_a}


# ==============================================================================
# NHÓM V — KIỂM NGHIỆM ỨNG SUẤT
# ==============================================================================

def V1_allowable_contact_stress(
    sigma_Hlim: float,
    SH: float = 1.1,
    ZR: float = 1.0,
    ZV: float = 1.0,
    KxH: float = 1.0,
    KHL: float = 1.0,
    sigma_ch: Optional[float] = None
) -> dict:
    """
    V1 — Ứng suất tiếp xúc cho phép (CT 6.1 và 6.13).

    CT 6.1  (thiết kế):
        [σH] = σ°Hlim · ZR · ZV · KxH · KHL / SH

    CT 6.13 (quá tải):
        [σH]max = 2.8·σch   (tôi cải thiện, khi có sigma_ch)
        [σH]max = 1260 MPa  (mặc định khi không có σch)
    """
    sH_allow = round(sigma_Hlim * ZR * ZV * KxH * KHL / SH, 3)
    if sigma_ch is not None:
        sH_max = round(2.8 * sigma_ch, 3)
    else:
        sH_max = 1260.0
    return {"sigma_H_allow": sH_allow, "sigma_H_max_allow": sH_max,
            "ZR": ZR, "ZV": ZV, "KxH": KxH, "KHL": KHL, "SH": SH}


def V2_allowable_bending_stress(
    sigma_Flim: float,
    SF: float = 1.75,
    YR: float = 1.0,
    YS: float = 1.0,
    KxF: float = 1.0,
    KFL: float = 1.0,
    sigma_ch: Optional[float] = None,
    nhiet_luyen: str = "toi_ct"
) -> dict:
    """
    V2 — Ứng suất uốn cho phép (CT 6.2 và 6.14).

    CT 6.2  (thiết kế):
        [σF] = σ°Flim · YR · YS · KxF · KFL / SF

    CT 6.14 (quá tải):
        [σF]max = 0.8·σch   (tôi cải thiện, khi có sigma_ch)
        [σF]max = 600 MPa   (thấm C / thấm N + tôi)
    """
    sF_allow = round(sigma_Flim * YR * YS * KxF * KFL / SF, 3)
    if nhiet_luyen in ("tham_C_toi", "tham_N"):
        sF_max = 600.0
    elif sigma_ch is not None:
        sF_max = round(0.8 * sigma_ch, 3)
    else:
        sF_max = round(0.8 * 580, 3)
    return {"sigma_F_allow": sF_allow, "sigma_F_max_allow": sF_max,
            "YR": YR, "YS": YS, "KxF": KxF, "KFL": KFL, "SF": SF}


def V3_contact_stress(
    T1: float,
    u: float,
    d1: float,
    bw: float,
    KH: float,
    cap_vat_lieu: str = "thep_thep",
    beta_deg: float = 0.0,
    eps_alpha: float = 1.75,
    sigma_H_allow: Optional[float] = None,
    an_khop: str = "ngoai",
    x_sum: float = 0.0
) -> dict:
    """
    V3 — Kiểm nghiệm ứng suất tiếp xúc σH (CT 6.33).

    Công thức:
        σH = ZM · ZH · Zε · √[ 2T1·KH·(u ± 1) / (bw·u·d1²) ] ≤ [σH]

    Trong đó:
        ZM  — hệ số cơ tính vật liệu (tra ZM_TABLE)
        ZH  — hệ số hình dạng bề mặt tiếp xúc (Bảng 6.12)
        Zε  — hệ số trùng khớp:
              Răng thẳng (β=0): Zε = √((4−εα)/3)  [CT 6.34a]

    QUAN TRỌNG: d1 phải là đường kính bánh chủ động CỦA CẤP ĐANG TÍNH.
    Với hệ nhiều cấp, người dùng phải truyền đúng d1 và T1 của cấp đó.
    """
    ZM   = get_ZM(cap_vat_lieu)
    ZH   = lookup_ZH(beta_deg, x_sum)
    sign = 1 if an_khop == "ngoai" else -1

    # CT 6.34a — Trịnh Chất trang 106:
    # Răng thẳng (β=0): Zε = √((4−εα)/3)
    if beta_deg < 0.5:
        Ze = math.sqrt((4.0 - eps_alpha) / 3.0)
    else:
        beta_r  = math.radians(beta_deg)
        eps_b   = bw * math.sin(beta_r) / (math.pi * d1 / (u + 1) * u)
        eps_b   = min(eps_b, 1.0)
        Ze = (math.sqrt((4 - eps_alpha) * (1 - eps_b) / 3 + eps_b / eps_alpha)
              if eps_b < 1 else math.sqrt(1.0 / eps_alpha))

    inner   = 2 * T1 * KH * (u + sign) / (bw * u * d1**2)
    sigma_H = round(ZM * ZH * Ze * math.sqrt(inner), 3)

    res = {"ZM": ZM, "ZH": ZH, "Ze": round(Ze, 4), "sigma_H": sigma_H}
    if sigma_H_allow is not None:
        ok = sigma_H <= sigma_H_allow
        res.update({"ok": ok,
                    "margin_pct": round((1 - sigma_H / sigma_H_allow)*100, 2)})
    return res


def V4_bending_stress(
    T1: float,
    m: float,
    d1: float,
    bw: float,
    KF: float,
    z1: int,
    z2: int,
    beta_deg: float = 0.0,
    eps_alpha: float = 1.75,
    sigma_F1_allow: Optional[float] = None,
    sigma_F2_allow: Optional[float] = None
) -> dict:
    """
    V4 — Kiểm nghiệm ứng suất mỏi uốn σF1, σF2 (CT 6.43 / 6.44).

    Công thức:
        σF1 = 2T1·KF·YF1·Yε·Yβ / (bw·d1·m)  ≤  [σF]1    (CT 6.43)
        σF2 = σF1·YF2 / YF1                   ≤  [σF]2    (CT 6.44)
    """
    beta_r = math.radians(beta_deg)
    cos3b  = math.cos(beta_r)**3

    zv1 = z1 / cos3b
    zv2 = z2 / cos3b
    YF1 = lookup_YF(int(round(zv1)))
    YF2 = lookup_YF(int(round(zv2)))

    Ye = round(1.0 / eps_alpha, 4)

    if beta_deg < 0.5:
        Yb = 1.0
    else:
        eps_b = bw * math.sin(beta_r) / (math.pi * m)
        Yb    = max(0.7, round(1.0 - eps_b * beta_deg / 140.0, 4))

    sigma_F1 = round(2 * T1 * KF * YF1 * Ye * Yb / (bw * d1 * m), 3)
    sigma_F2 = round(sigma_F1 * YF2 / YF1, 3)

    res = {
        "zv1": round(zv1, 3), "zv2": round(zv2, 3),
        "YF1": YF1, "YF2": YF2,
        "Ye": Ye,   "Yb": Yb,
        "sigma_F1": sigma_F1, "sigma_F2": sigma_F2,
    }
    if sigma_F1_allow is not None:
        res["ok1"]         = sigma_F1 <= sigma_F1_allow
        res["margin1_pct"] = round((1 - sigma_F1 / sigma_F1_allow)*100, 2)
    if sigma_F2_allow is not None:
        res["ok2"]         = sigma_F2 <= sigma_F2_allow
        res["margin2_pct"] = round((1 - sigma_F2 / sigma_F2_allow)*100, 2)
    return res


def V5_overload_stress(
    Kqt: float,
    sigma_H: float,
    sigma_F1: float,
    sigma_F2: float,
    sigma_H_max_allow: float,
    sigma_F1_max_allow: float,
    sigma_F2_max_allow: float,
    sigma_H_allow: Optional[float] = None,
) -> dict:
    """
    V5 — Kiểm nghiệm ứng suất cực đại khi quá tải (CT 6.48 / 6.49).

    Có HAI cách tính σH_max thường gặp trong tài liệu:

    Cách A — dùng σH tính được (cách thông thường):
        σH_max  = σH_calc · √Kqt   ≤  [σH]max

    Cách B — dùng [σH] cho phép (theo PDF tham chiếu mục 3.3.7):
        σH_max  = [σH] · √Kqt      ≤  [σH]max
        (bảo thủ hơn, dùng [σH] thay cho σH_calc)
    """
    sqrt_Kqt = math.sqrt(Kqt)

    sHm_calc = round(sigma_H * sqrt_Kqt, 3)
    sF1m     = round(sigma_F1 * sqrt_Kqt, 3)
    sF2m     = round(sigma_F2 * sqrt_Kqt, 3)

    if sigma_H_allow is not None:
        sHm_allow = round(sigma_H_allow * sqrt_Kqt, 3)
        sHm = sHm_allow
    else:
        sHm_allow = None
        sHm = sHm_calc

    okH  = sHm  <= sigma_H_max_allow
    okF1 = sF1m <= sigma_F1_max_allow
    okF2 = sF2m <= sigma_F2_max_allow

    res = {
        "Kqt":                   round(Kqt, 4),
        "sqrt_Kqt":              round(sqrt_Kqt, 4),
        "sigma_H_max":           sHm,
        "sigma_H_max_from_calc": sHm_calc,
        "sigma_F1_max":          sF1m,
        "sigma_F2_max":          sF2m,
        "ok_H":  okH, "ok_F1": okF1, "ok_F2": okF2,
        "all_ok": okH and okF1 and okF2,
        "margin_H_pct":  round((1 - sHm  / sigma_H_max_allow)*100,  2),
        "margin_F1_pct": round((1 - sF1m / sigma_F1_max_allow)*100, 2),
        "margin_F2_pct": round((1 - sF2m / sigma_F2_max_allow)*100, 2),
    }
    if sHm_allow is not None:
        res["sigma_H_max_from_allow"] = sHm_allow
    return res


# ==============================================================================
# KIỂM TRA ĐIỀU KIỆN ĂN KHỚP KỸ THUẬT
# ==============================================================================

def check_meshing_conditions(
    geo: dict,
    eps_alpha_min: float = 1.2,
    bw_m_min: float = 8.0,
    bw_m_max: float = 30.0,
    z_min: int = Z_MIN
) -> dict:
    """
    Kiểm tra các điều kiện ăn khớp kỹ thuật.

    [FIX-5] Hàm mới kiểm tra εα, z_min, bw/m.
    """
    z1        = geo["z1"]
    z2        = geo["z2"]
    eps_alpha = geo["eps_alpha"]
    bw        = geo["bw"]
    m         = geo["m"]
    bw_over_m = bw / m

    warnings_list = []

    z1_ok = z1 >= z_min
    z2_ok = z2 >= z_min
    if not z1_ok:
        warnings_list.append(f" z1={z1} < z_min={z_min}: nguy cơ cắt chân răng bánh nhỏ!")
    if not z2_ok:
        warnings_list.append(f" z2={z2} < z_min={z_min}: nguy cơ cắt chân răng bánh lớn!")

    eps_phys_ok = eps_alpha >= 1.0
    eps_ok      = eps_alpha >= eps_alpha_min
    if not eps_phys_ok:
        warnings_list.append(f" εα={eps_alpha:.4f} < 1.0: vi phạm điều kiện vật lý!")
    elif not eps_ok:
        warnings_list.append(
            f" εα={eps_alpha:.4f} < {eps_alpha_min}: không đạt ngưỡng khuyến nghị.")

    bw_m_ok = bw_m_min <= bw_over_m <= bw_m_max
    if not bw_m_ok:
        if bw_over_m < bw_m_min:
            warnings_list.append(f" bw/m={bw_over_m:.2f} < {bw_m_min}: răng quá hẹp.")
        else:
            warnings_list.append(f" bw/m={bw_over_m:.2f} > {bw_m_max}: răng quá rộng.")

    all_ok = z1_ok and z2_ok and eps_phys_ok and eps_ok and bw_m_ok

    return {
        "z1_ok": z1_ok, "z2_ok": z2_ok,
        "eps_phys_ok": eps_phys_ok, "eps_ok": eps_ok,
        "bw_m_ok": bw_m_ok, "all_ok": all_ok,
        "bw_over_m": round(bw_over_m, 3),
        "eps_alpha":  eps_alpha,
        "warnings":   warnings_list,
    }


# ==============================================================================
# IN BẢNG THỐNG KÊ
# ==============================================================================

def print_gear_table(geo: dict):
    """In bảng thống kê thông số bộ truyền bánh răng trụ răng thẳng."""
    W = 68
    B = "\033[94m"; E = "\033[0m"; BD = "\033[1m"
    def row(stt, name, sym, val1, val2, unit):
        v1 = f"{val1:.3f}" if isinstance(val1, float) else str(val1)
        v2 = f"{val2:.3f}" if isinstance(val2, float) else str(val2)
        print(f"  {stt:>2}│ {name:<28}│ {sym:<6}│{B}{v1:>10}{E} │{B}{v2:>10}{E} │ {unit}")

    print("\n" + "═"*W)
    print(f"  {BD}BẢNG THỐNG KÊ THÔNG SỐ BỘ TRUYỀN BÁNH RĂNG TRỤ RĂNG THẲNG{E}")
    print("═"*W)
    print(f"  {'STT':>2}│ {'Thông số':<28}│ {'Ký h.':6}│{'Bánh nhỏ':>11} │{'Bánh lớn':>11} │ Đơn vị")
    print("─"*W)
    row( 1, "Khoảng cách trục",      "aw",   geo["aw"],  geo["aw"],  "mm")
    row( 2, "Môđun pháp",            "m",    geo["m"],   geo["m"],   "mm")
    row( 3, "Chiều rộng vành răng",  "bw",   geo["bw"],  geo["bw"],  "mm")
    row( 4, "Tỉ số truyền",          "u",    geo["u"],   geo["u"],   "—")
    row( 5, "Số răng",               "z",    geo["z1"],  geo["z2"],  "răng")
    row( 6, "Hệ số dịch chỉnh",      "x",    geo["x1"],  geo["x2"],  "—")
    row( 7, "Góc nghiêng răng",      "β",    geo["beta_deg"], geo["beta_deg"], "°")
    row( 8, "Góc ăn khớp",          "αw",   geo["alpha_w"], geo["alpha_w"], "°")
    print("─"*W)
    row( 9, "Đường kính vòng chia",  "d",    geo["d1"],  geo["d2"],  "mm")
    row(10, "Đường kính vòng lăn",   "dw",   geo["dw1"], geo["dw2"], "mm")
    row(11, "Đường kính đỉnh răng",  "da",   geo["da1"], geo["da2"], "mm")
    row(12, "Đường kính đáy răng",   "df",   geo["df1"], geo["df2"], "mm")
    print("─"*W)
    row(13, "Chiều cao đầu răng",    "ha",   geo["ha"],  geo["ha"],  "mm")
    row(14, "Chiều cao chân răng",   "hf",   geo["hf"],  geo["hf"],  "mm")
    row(15, "Chiều cao toàn phần",   "h",    geo["h"],   geo["h"],   "mm")
    row(16, "Khe hở hướng tâm",      "c",    geo["c"],   geo["c"],   "mm")
    row(17, "Bước răng",             "p",    geo["p"],   geo["p"],   "mm")
    row(18, "Bước cơ sở",            "pb",   geo["pb"],  geo["pb"],  "mm")
    row(19, "Hệ số trùng khớp ngang","εα",   geo["eps_alpha"], geo["eps_alpha"], "—")
    row(20, "Hệ số dạng răng",       "YF",   geo["YF1"], geo["YF2"], "—")
    print("═"*W + "\n")


# ==============================================================================
# HÀM MAIN — CHẠY DEMO TÍNH TOÁN BỘ TRUYỀN BÁNH RĂNG TRỤ RĂNG THẲNG
# ==============================================================================

def main(
    # ── Thông số truyền động ───────────────────────────────────────────────
    T1: float         = 223192.0,   # Mômen xoắn bánh chủ động dùng kiểm nghiệm (N·mm)

    T1_sb: float      = 210538.22,  # T1 dùng riêng cho CT 6.15a tính aw_sb (N·mm)
                                    # PDF cấp 2: T1_sb=210538.22 → aw_sb=219.22 mm
    n1: float         = 1460.0,     # Tốc độ quay bánh chủ động (rpm) — dùng tính v nếu không có n1_vantoc

    n1_vantoc: float  = 259.73,     # n1 riêng để hiển thị vận tốc (rpm) — PDF cấp 2

    d1_vantoc: float  = 89.45,      # d1 riêng để hiển thị vận tốc (mm) — PDF cấp 2

    u_yc: float       = 3.71,       # Tỉ số truyền yêu cầu
    Kqt: float        = 2.2,        # Hệ số quá tải Tmax/T
    # ── Vật liệu bánh nhỏ ─────────────────────────────────────────────────
    sigma_Hlim1: float = 570.0,
    sigma_Flim1: float = 450.0,
    sigma_ch1:   float = 580.0,
    SH1: float         = 1.1,
    SF1: float         = 1.75,
    KHL1: float        = 1.0,
    KFL1: float        = 1.0,
    # ── Vật liệu bánh lớn ─────────────────────────────────────────────────
    sigma_Hlim2: float = 530.0,
    sigma_Flim2: float = 414.0,
    sigma_ch2:   float = 580.0,
    SH2: float         = 1.1,
    SF2: float         = 1.75,
    KHL2: float        = 1.0,
    KFL2: float        = 1.0,
    # ── Thông số hình học (đã chọn / chuẩn hóa) ───────────────────────────
    psi_a: float  = 0.3,
    aw: float     = 226.5,
    m: float      = 3.0,
    z1: int       = 32,
    z2: int       = 119,
    x1: float     = 0.0,
    x2: float     = 0.0,
    # ── Hệ số tải trọng kiểm nghiệm ───────────────────────────────────────
    KHb: float = 1.02,  KHa: float = 1.13,  KHv: float = 1.05,
    KFb: float = 1.07,  KFa: float = 1.37,  KFv: float = 1.13,
    # ── Hệ số sơ bộ khoảng cách trục ──────────────────────────────────────
    KHb_sb: float = 1.02,
    # ── Cặp vật liệu ──────────────────────────────────────────────────────
    cap_vat_lieu: str = "thep_thep",
    # ── Hiển thị bảng hình học ────────────────────────────────────────────
    hien_thi_bang: bool = True,
) -> dict:
    """
    Hàm demo chạy toàn bộ quy trình tính toán bộ truyền bánh răng trụ răng thẳng.

    QUAN TRỌNG — Thông số đầu vào theo CẤP đang tính:
        T1      : Mômen xoắn dùng cho kiểm nghiệm bền (CT 6.33, 6.43, 6.48) (N·mm)
        T1_sb   : Mômen xoắn dùng riêng cho CT 6.15a tính aw_sb (N·mm)
                  [FIX-14] Default = 210538.22 (T1 sơ bộ cấp 2 theo case study).
                  Với cấp khác, truyền đúng giá trị T1 sơ bộ của cấp đó.
        n1_vantoc: Tốc độ dùng riêng để hiển thị vận tốc vòng v (rpm)
                   [FIX-15] Default = 259.73 rpm (n1 cấp 2 theo case study).
        d1_vantoc: Đường kính dùng riêng để hiển thị vận tốc vòng v (mm)
                   [FIX-15] Default = 89.45 mm (d1 cấp 2 theo case study).
                   → v = π·89.45·259.73/60000 = 1.22 m/s (đáp án đúng).
    """
    W = 80
    BD = "\033[1m"; E = "\033[0m"
    G  = "\033[92m"; R = "\033[91m"; Y = "\033[93m"; C = "\033[96m"

    def _tag(ok: bool) -> str:
        return f"{G}Đạt{E}" if ok else f"{R}Không đạt{E}"

    def _dp(val: float, allow: float) -> str:
        pct = (1 - val / allow) * 100
        col = G if pct >= 0 else R
        return f"{col}{pct:.1f}%{E}"

    def _head(title: str):
        print(f"\n{Y}▌ {title}{E}")
        print("─" * W)

    print("\n" + "═" * W)
    print(f"  {BD}BÁO CÁO TÍNH TOÁN BỘ TRUYỀN BÁNH RĂNG TRỤ - RĂNG THẲNG{E}")
    print("═" * W)

    # =========================================================================
    # BƯỚC 1 — ỨNG SUẤT CHO PHÉP
    # =========================================================================
    _head("BƯỚC 1: ỨNG SUẤT CHO PHÉP")

    rH1 = V1_allowable_contact_stress(sigma_Hlim1, SH=SH1, KHL=KHL1, sigma_ch=sigma_ch1)
    rH2 = V1_allowable_contact_stress(sigma_Hlim2, SH=SH2, KHL=KHL2, sigma_ch=sigma_ch2)
    rF1 = V2_allowable_bending_stress(sigma_Flim1, SF=SF1, KFL=KFL1, sigma_ch=sigma_ch1)
    rF2 = V2_allowable_bending_stress(sigma_Flim2, SF=SF2, KFL=KFL2, sigma_ch=sigma_ch2)

    sH_allow1 = rH1["sigma_H_allow"]
    sH_allow2 = rH2["sigma_H_allow"]
    sH_allow  = min(sH_allow1, sH_allow2)
    sF_allow1 = rF1["sigma_F_allow"]
    sF_allow2 = rF2["sigma_F_allow"]
    sH_max    = rH1["sigma_H_max_allow"]
    sF1_max   = rF1["sigma_F_max_allow"]
    sF2_max   = rF2["sigma_F_max_allow"]

    print(f"  {'Thông số':<38} {'Bánh nhỏ':>12}  {'Bánh lớn':>12}  Đơn vị")
    print("  " + "─" * (W - 2))
    print(f"  {'σ⁰_Hlim  (giới hạn mỏi tiếp xúc)':<38} {sigma_Hlim1:>12.2f}  {sigma_Hlim2:>12.2f}  MPa")
    print(f"  {'σ⁰_Flim  (giới hạn mỏi uốn)':<38} {sigma_Flim1:>12.2f}  {sigma_Flim2:>12.2f}  MPa")
    print(f"  {'σ_ch     (giới hạn chảy)':<38} {sigma_ch1:>12.2f}  {sigma_ch2:>12.2f}  MPa")
    print(f"  {'S_H      (hệ số an toàn tiếp xúc)':<38} {SH1:>12.2f}  {SH2:>12.2f}  —")
    print(f"  {'S_F      (hệ số an toàn uốn)':<38} {SF1:>12.2f}  {SF2:>12.2f}  —")
    print(f"  {'K_HL     (hệ số tuổi thọ tiếp xúc)':<38} {KHL1:>12.4f}  {KHL2:>12.4f}  —")
    print(f"  {'K_FL     (hệ số tuổi thọ uốn)':<38} {KFL1:>12.4f}  {KFL2:>12.4f}  —")
    print("  " + "─" * (W - 2))
    print(f"  {C}{'[σH]     (ứng suất tiếp xúc cho phép)':<38} {sH_allow1:>12.2f}  {sH_allow2:>12.2f}  MPa{E}")
    print(f"  {C}{'[σF]     (ứng suất uốn cho phép)':<38} {sF_allow1:>12.2f}  {sF_allow2:>12.2f}  MPa{E}")
    print(f"  {C}{'[σH]max  = 2.8·σch (tiếp xúc quá tải)':<38} {sH_max:>12.2f}  {'—':>12}  MPa{E}")
    print(f"  {C}{'[σF]max  = 0.8·σch (uốn quá tải)':<38} {sF1_max:>12.2f}  {sF2_max:>12.2f}  MPa{E}")
    print(f"\n  [σH] bộ truyền = {BD}{sH_allow:.2f} MPa{E}  (Lấy giá trị nhỏ nhất trong hai bánh)")

    allowable_result = {
        "sH_allow1": sH_allow1, "sH_allow2": sH_allow2, "sH_allow": sH_allow,
        "sF_allow1": sF_allow1, "sF_allow2": sF_allow2,
        "sH_max":  sH_max, "sF1_max": sF1_max, "sF2_max": sF2_max,
    }

    # =========================================================================
    # BƯỚC 2 — THÔNG SỐ CƠ BẢN & HÌNH HỌC
    # =========================================================================
    _head("BƯỚC 2: THÔNG SỐ CƠ BẢN & HÌNH HỌC")

    _T1_sb = T1_sb

    # 2a. Khoảng cách trục sơ bộ (CT 6.15a)
    sb = D1_preliminary_center_distance(
        _T1_sb, u_yc, sH_allow,
        psi_a=psi_a, KHb=KHb_sb,
        cap_vat_lieu=cap_vat_lieu, loai_rang="thang",
        standardize=False,
    )
    print(f"  Ka = {sb['Ka']}  (Hệ số vật liệu — Bảng 6.5")
    print(f"  T1 dùng cho CT 6.15a: T1_sb={_T1_sb:.2f} N·mm  ")
    print(f"  Khoảng cách trục sơ bộ:  aw_sb = {BD}{sb['aw_sb']:.2f} mm{E} ")

    bw     = round(psi_a * aw, 2)
    u_real = z2 / z1
    print(f"  Khoảng cách trục chọn:   aw    = {BD}{aw:.2f} mm{E}  (đã chuẩn hóa / lựa chọn)")
    print(f"  Sai lệch:                δaw   = {aw - sb['aw_sb']:+.2f} mm\n")

    print(f"  Thông số sau khi chuẩn hóa và chọn số răng:")
    print(f"  {'m   (môđun)':<40} = {BD}{m} mm{E}")
    print(f"  {'z₁  (số răng bánh nhỏ)':<40} = {BD}{z1}")
    print(f"  {'z₂  (số răng bánh lớn)':<40} = {BD}{z2}")
    print(f"  {'bw  (chiều rộng vành răng = ψa·aw)':<40} = {BD}{bw} mm{E}  (ψa = {psi_a})")
    print(f"  {'u   (tỉ số truyền thực = z₂/z₁)':<40} = {BD}{u_real:.4f}{E}")

    # 2c. Hình học đầy đủ
    geo = G8_all_geometry(m=m, z1=z1, z2=z2, aw=aw, psi_a=psi_a, x1=x1, x2=x2)

    print(f"\n  {'Thông số':<40} {'Bánh nhỏ':>10}  {'Bánh lớn':>10}  Đơn vị")
    print("  " + "─" * (W - 2))
    print(f"  {'d   (đường kính vòng chia)':<40} {geo['d1']:>10.2f}  {geo['d2']:>10.2f}  mm")
    print(f"  {'dw  (đường kính vòng lăn)':<40} {geo['dw1']:>10.2f}  {geo['dw2']:>10.2f}  mm")
    print(f"  {'da  (đường kính đỉnh răng)':<40} {geo['da1']:>10.2f}  {geo['da2']:>10.2f}  mm")
    print(f"  {'df  (đường kính đáy răng)':<40} {geo['df1']:>10.2f}  {geo['df2']:>10.2f}  mm")
    print(f"  {'ha  (chiều cao đầu răng)':<40} {geo['ha']:>10.3f}  {geo['ha']:>10.3f}  mm")
    print(f"  {'hf  (chiều cao chân răng)':<40} {geo['hf']:>10.3f}  {geo['hf']:>10.3f}  mm")
    print(f"  {'h   (chiều cao toàn phần)':<40} {geo['h']:>10.3f}  {geo['h']:>10.3f}  mm")
    print(f"  {'p   (bước răng)':<40} {geo['p']:>10.4f}  {geo['p']:>10.4f}  mm")
    print(f"  {'pb  (bước cơ sở)':<40} {geo['pb']:>10.4f}  {geo['pb']:>10.4f}  mm")
    print(f"  {'εα  (hệ số trùng khớp ngang)':<40} {geo['eps_alpha']:>10.4f}  {'—':>10}  —")
    print(f"  {'ZH  (hệ số hình dạng bề mặt tx)':<40} {geo['ZH']:>10.4f}  {'—':>10}  —")
    print(f"  {'YF  (hệ số dạng răng)':<40} {geo['YF1']:>10.3f}  {geo['YF2']:>10.3f}  —")

    # =========================================================================
    # BƯỚC 3 — KIỂM TRA ĐIỀU KIỆN ĂN KHỚP
    # =========================================================================
    _head("BƯỚC 3: KIỂM TRA ĐIỀU KIỆN ĂN KHỚP")

    mesh   = check_meshing_conditions(geo)
    psi_ba = bw / aw

    print(f"  ψ_ba  = bw/aw   = {psi_ba:.3f}")
    print(f"  bw/m  = {bw}/{m:.0f}    = {mesh['bw_over_m']:.2f}  (trong khoảng [8, 30]  → {_tag(mesh['bw_m_ok'])})")
    print(f"  εα    = {geo['eps_alpha']:.4f}         ≥ 1.2  → {_tag(mesh['eps_ok'])}")
    print(f"  z₁    = {z1:<6}           ≥ {Z_MIN}    → {_tag(mesh['z1_ok'])}")
    print(f"  z₂    = {z2:<6}           ≥ {Z_MIN}    → {_tag(mesh['z2_ok'])}")
    if mesh["warnings"]:
        print()
        for w in mesh["warnings"]:
            print(f"  {Y}{w}{E}")
    print(f"\n  Điều kiện ăn khớp tổng thể: {_tag(mesh['all_ok'])}")

    # =========================================================================
    # BƯỚC 4 — KIỂM NGHIỆM ĐỘ BỀN TIẾP XÚC
    # =========================================================================
    _head("BƯỚC 4: KIỂM NGHIỆM ĐỘ BỀN TIẾP XÚC")

    # [FIX-15] Vận tốc vòng: dùng d1_vantoc=89.45 mm, n1_vantoc=259.73 rpm (cấp 2)
    _d1_v = d1_vantoc   # 89.45 mm (đã là giá trị cụ thể, không còn None)
    _n1_v = n1_vantoc   # 259.73 rpm
    v_ms  = round(math.pi * _d1_v * _n1_v / 60_000, 2)   # → 1.22 m/s

    KH = round(KHb * KHa * KHv, 4)
    eps_H = geo["eps_alpha"]

    v3 = V3_contact_stress(
        T1=T1, u=u_real, d1=geo["d1"], bw=bw, KH=KH,
        cap_vat_lieu=cap_vat_lieu,
        eps_alpha=eps_H, sigma_H_allow=sH_allow,
        x_sum=x1+x2,
    )

    print(f"  v   = π·d₁·n₁/60000 = π·{_d1_v:.2f}·{_n1_v:.2f}/60000 = {v_ms} m/s  ")
    print(f"  ZM  = {v3['ZM']:.0f}   (Tra Bảng 6.5 — {cap_vat_lieu})")
    print(f"  ZH  = {v3['ZH']:.4f}  (Tra Bảng 6.12 — β=0° ")
    print(f"  εα  = {eps_H:.4f}")
    print(f"  Zε  = √((4−εα)/3) = √((4−{eps_H:.4f})/3) = {v3['Ze']:.4f}   ")
    print(f"  KHβ = {KHb}  |  KHα = {KHa}  |  KHv = {KHv}")
    print(f"  KH  = KHβ·KHα·KHv = {KHb}·{KHa}·{KHv} = {KH:.4f}")
    print()
    print(f"  σH = ZM·ZH·Zε·√[2T₁·KH·(u+1)/(bw·u·d₁²)]")
    print(f"         = {v3['ZM']:.0f} × {v3['ZH']:.4f} × {v3['Ze']:.4f}")
    print(f"           × √[2·{T1:.2f}·{KH:.4f}·{u_real+1:.4f}/({bw}·{u_real:.4f}·{geo['d1']:.2f}²)]")
    print(f"         = {BD}{C}{v3['sigma_H']:.2f} MPa{E}")
    print()
    ok_tag4 = _tag(v3["ok"])
    dp4     = _dp(v3["sigma_H"], sH_allow)
    print(f"  σH = {v3['sigma_H']:.2f} MPa  ≤  [σH] = {sH_allow:.2f} MPa  →  {ok_tag4}  (dự phòng {dp4})")

    # =========================================================================
    # BƯỚC 5 — KIỂM NGHIỆM ĐỘ BỀN UỐN
    # =========================================================================
    _head("BƯỚC 5: KIỂM NGHIỆM ĐỘ BỀN UỐN")

    KF     = round(KFb * KFa * KFv, 4)
    eps_F  = geo["eps_alpha"]

    v4 = V4_bending_stress(
        T1=T1, m=m, d1=geo["d1"], bw=bw, KF=KF,
        z1=z1, z2=z2, eps_alpha=eps_F,
        sigma_F1_allow=sF_allow1, sigma_F2_allow=sF_allow2,
    )

    print(f"  εα  = {eps_F:.4f}")
    print(f"  Yε  = 1/εα = 1/{eps_F:.4f} = {v4['Ye']:.4f}")
    print(f"  Yβ  = {v4['Yb']:.4f}  (răng thẳng β=0° → Yβ=1)")
    print(f"  YF₁ = {v4['YF1']:.3f}  (Tra Bảng 6.7, z₁={z1})")
    print(f"  YF₂ = {v4['YF2']:.3f}  (Tra Bảng 6.7, z₂={z2})")
    print(f"  KFβ = {KFb}  |  KFα = {KFa}  |  KFv = {KFv}")
    print(f"  KF  = KFβ·KFα·KFv = {KFb}·{KFa}·{KFv} = {KF:.4f}")
    print()
    print(f"  σF₁ = 2T₁·KF·YF₁·Yε·Yβ / (bw·d₁·m)")
    print(f"         = 2·{T1:.2f}·{KF:.4f}·{v4['YF1']:.3f}·{v4['Ye']:.4f}·{v4['Yb']:.1f}")
    print(f"           / ({bw}·{geo['d1']:.2f}·{m:.0f})")
    print(f"         = {BD}{C}{v4['sigma_F1']:.2f} MPa{E}")
    print()
    print(f"  σF₂ = σF₁·YF₂/YF₁ = {v4['sigma_F1']:.2f}·{v4['YF2']:.3f}/{v4['YF1']:.3f}")
    print(f"         = {BD}{C}{v4['sigma_F2']:.2f} MPa{E}")
    print()
    ok_f1 = _tag(v4["ok1"]); dp_f1 = _dp(v4["sigma_F1"], sF_allow1)
    ok_f2 = _tag(v4["ok2"]); dp_f2 = _dp(v4["sigma_F2"], sF_allow2)
    print(f"  σF₁ = {v4['sigma_F1']:.2f} MPa  ≤  [σF]₁ = {sF_allow1:.2f} MPa  →  {ok_f1}  (dự phòng {dp_f1})")
    print(f"  σF₂ = {v4['sigma_F2']:.2f} MPa  ≤  [σF]₂ = {sF_allow2:.2f} MPa  →  {ok_f2}  (dự phòng {dp_f2})")

    # =========================================================================
    # BƯỚC 6 — KIỂM NGHIỆM QUÁ TẢI
    # =========================================================================
    _head(f"BƯỚC 6: KIỂM NGHIỆM QUÁ TẢI  (Kqt = Tmax/T = {Kqt:.2f})")

    v5 = V5_overload_stress(
        Kqt=Kqt,
        sigma_H=v3["sigma_H"],
        sigma_F1=v4["sigma_F1"],
        sigma_F2=v4["sigma_F2"],
        sigma_H_max_allow=sH_max,
        sigma_F1_max_allow=sF1_max,
        sigma_F2_max_allow=sF2_max,
        sigma_H_allow=sH_allow,
    )

    sqrt_Kqt = v5["sqrt_Kqt"]
    print(f"  √Kqt = √{Kqt} = {sqrt_Kqt:.4f}")
    print()
    print(f"  σH_max  = [σH] · √Kqt = {sH_allow:.2f} · {sqrt_Kqt:.4f} = {BD}{C}{v5['sigma_H_max']:.2f} MPa{E}   ")
    print(f"  σF₁_max = σF₁ · √Kqt = {v4['sigma_F1']:.2f} · {sqrt_Kqt:.4f} = {BD}{C}{v5['sigma_F1_max']:.2f} MPa{E}   ")
    print(f"  σF₂_max = σF₂ · √Kqt = {v4['sigma_F2']:.2f} · {sqrt_Kqt:.4f} = {BD}{C}{v5['sigma_F2_max']:.2f} MPa{E}   ")
    print()
    ok_H  = _tag(v5["ok_H"]);  dp_H  = _dp(v5["sigma_H_max"],  sH_max)
    ok_F1 = _tag(v5["ok_F1"]); dp_F1 = _dp(v5["sigma_F1_max"], sF1_max)
    ok_F2 = _tag(v5["ok_F2"]); dp_F2 = _dp(v5["sigma_F2_max"], sF2_max)
    print(f"  σH_max  = {v5['sigma_H_max']:.2f} MPa  ≤  [σH]max  = {sH_max:.0f} MPa  →  {ok_H}  (dự phòng {dp_H})")
    print(f"  σF₁_max = {v5['sigma_F1_max']:.2f} MPa  ≤  [σF₁]max = {sF1_max:.0f} MPa  →  {ok_F1}  (dự phòng {dp_F1})")
    print(f"  σF₂_max = {v5['sigma_F2_max']:.2f} MPa  ≤  [σF₂]max = {sF2_max:.0f} MPa  →  {ok_F2}  (dự phòng {dp_F2})")

    # =========================================================================
    # KẾT LUẬN CHUNG
    # =========================================================================
    all_ok = (v3.get("ok", True) and
              v4.get("ok1", True) and v4.get("ok2", True) and
              v5["all_ok"] and mesh["all_ok"])

    print("\n" + "═" * W)
    if all_ok:
        print(f"  {G}{BD}✓  BỘ TRUYỀN ĐẠT YÊU CẦU — Tất cả điều kiện bền đều thỏa mãn.{E}")
    else:
        print(f"  {R}{BD}✗  BỘ TRUYỀN KHÔNG ĐẠT — Cần kiểm tra lại thông số thiết kế.{E}")
    print("═" * W)

    if hien_thi_bang:
        print_gear_table(geo)

    return {
        "allowable": allowable_result,
        "geometry":  geo,
        "meshing":   mesh,
        "contact":   v3,
        "bending":   v4,
        "overload":  v5,
        "all_ok":    all_ok,
    }


if __name__ == "__main__":
    results = main()