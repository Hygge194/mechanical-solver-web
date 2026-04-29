"""
=============================================================================
THIẾT KẾ BỘ TRUYỀN BÁNH RĂNG CÔN – RĂNG THẲNG
Hệ thống dẫn động thùng trộn
=============================================================================
Tài liệu tham khảo: Tính toán thiết kế hệ dẫn động cơ khí – Trịnh Chất & Lê Văn Uyển
=============================================================================

BUG-FIX LOG (8 lỗi đã sửa):
──────────────────────────────────────────────────────────────────────────────
BUG 1 (b cập nhật sai trong vòng lặp module):
  Code cũ: mỗi lần tăng mte, gán lại b = K_be × Re_mới → b phồng to.
  Fix: b = K_be × Re_sb (cố định từ ban đầu, không thay đổi theo mte).

BUG 2 (công thức vH dùng sqrt(dm1/u) sai – CT 6.64 Trịnh Chất):
  Code cũ: vH = delta_H * g0 * v * sqrt(dm1 / u)
  Fix:     vH = delta_H * g0 * v * sqrt(dm1 * (u + 1) / u)

BUG 3 (công thức σH sai – CT 6.58 Trịnh Chất):
  Công thức đúng trong sách: nen = 2*T1*KH*sqrt(u²+1) / (0.85*b*u*dm1²)
    → sqrt(u²+1) nằm BÊN TRONG biểu thức dưới dấu căn lớn (nested sqrt),
      mẫu số chỉ có u (không phải u²).
  Code cũ sai lần 1: nen = ... / (0.85 * b * u  * dm1²)  → thiếu sqrt
  Code cũ sai lần 2: nen = ... / (0.85 * b * u² * dm1²)  → u² thay vì u

BUG 4 (công thức vF sai tương tự vH – CT 6.68a):
  Code cũ: vF = delta_F * g0 * v * sqrt(dm1 / u)
  Fix:     vF = delta_F * g0 * v * sqrt(dm1 * (u + 1) / u)

BUG 5 (công thức σF dùng mte và bỏ hệ số 0.85 – CT 6.65 Trịnh Chất):
  Code cũ: σF1 = Ft * KF * Yε * YF1 / (b * mte)
  Fix:     σF1 = 2*T1 * KF * Yε * YF1 / (0.85 * b * mtm * dm1)

BUG 6 (K_qt hardcode = 1.4 thay vì giá trị đề bài):
  Fix: K_qt mặc định = 2.2.

BUG 7 (K_Fbeta dùng sai – phải tra bảng 6.21 riêng theo K_be*u/(2-K_be)):
  Code cũ: K_Fbeta = K_Hbeta (lấy cùng giá trị hệ số tiếp xúc).
  Fix: K_Fbeta tra bảng 6.21 theo tham số x = K_be*u/(2-K_be), nội suy
       từ cột K_Fβ (sơ đồ I, loại răng thẳng, HB≤350). K_Fbeta ≠ K_Hbeta.

BUG 8 (n1 trong demo main dùng tốc độ động cơ thay vì tốc độ trục bánh côn):
  Code cũ: n1 = 980.0  (rpm động cơ)
  Fix:     n1 = 1168.8 (rpm trục 1 vào bánh côn nhỏ, sau bộ truyền đai).
  Lưu ý: hàm thiet_ke_banh_rang_con nhận n1 = tốc độ trục VÀO bánh côn,
          không phải tốc độ động cơ.
──────────────────────────────────────────────────────────────────────────────
"""

import math
from dataclasses import dataclass, field
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# BẢNG TRA DỮ LIỆU
# ─────────────────────────────────────────────────────────────────────────────

BANG_6_2 = {
    "thuong_hoa_toi_cai_thien": {
        "mo_ta": "Thường hóa hoặc tôi cải thiện (HB 180–350 / HRC 45–35)",
        "sigma_Hlim_func": lambda hardness: 2 * hardness + 70,
        "S_H": 1.1,
        "sigma_Flim_func": lambda hardness: 1.8 * hardness,
        "S_F": 1.75,
    },
    "toi_the_tich": {
        "mo_ta": "Tôi thể tích (HRC 45–55)",
        "sigma_Hlim_func": lambda HRC: 18 * HRC + 150,
        "S_H": 1.1,
        "sigma_Flim_func": lambda HRC: 550,
        "S_F": 1.75,
    },
    "toi_be_mat_m_lon": {
        "mo_ta": "Tôi bề mặt bằng dòng điện tần số cao (mn ≥ 3 mm)",
        "sigma_Hlim_func": lambda HRCm: 17 * HRCm + 200,
        "S_H": 1.2,
        "sigma_Flim_func": lambda HRC: 900,
        "S_F": 1.75,
    },
    "toi_be_mat_m_nho": {
        "mo_ta": "Tôi bề mặt bằng dòng điện tần số cao (mn < 3 mm)",
        "sigma_Hlim_func": lambda HRCm: 17 * HRCm + 200,
        "S_H": 1.2,
        "sigma_Flim_func": lambda HRC: 550,
        "S_F": 1.75,
    },
    "tham_cacbon_toi": {
        "mo_ta": "Thấm cacbon và tôi (HRC 55–63 / HRC 30–45)",
        "sigma_Hlim_func": lambda HRCm: 23 * HRCm,
        "S_H": 1.2,
        "sigma_Flim_func": lambda HRC: 750,
        "S_F": 1.55,
    },
    "tham_cacbon_molipden": {
        "mo_ta": "Thấm cacbon và tôi – thép molipden (25XГM, 25XГHM)",
        "sigma_Hlim_func": lambda HRCm: 23 * HRCm,
        "S_H": 1.2,
        "sigma_Flim_func": lambda HRC: 1000,
        "S_F": 1.55,
    },
    "tham_nito_toi": {
        "mo_ta": "Thấm nitơ và tôi (HRC 55–67 / HRC 24–40)",
        "sigma_Hlim_func": lambda HRC: 1050,
        "S_H": 1.2,
        "sigma_Flim_func": lambda HRCI: 12 * HRCI + 30,
        "S_F": 1.75,
    },
}

BANG_6_4 = {
    0: {"K_HE": 1.000, "K_FE_toi_cai_thien_mF6": 1.000,
        "K_FE_thuong_hoa_thamN_mF6": 1.000, "K_FE_toi_the_tich_bemat_thamC_mF9": 1.000},
    1: {"K_HE": 0.500, "K_FE_toi_cai_thien_mF6": 0.300,
        "K_FE_thuong_hoa_thamN_mF6": 0.300, "K_FE_toi_the_tich_bemat_thamC_mF9": 0.200},
    2: {"K_HE": 0.250, "K_FE_toi_cai_thien_mF6": 0.140,
        "K_FE_thuong_hoa_thamN_mF6": 0.140, "K_FE_toi_the_tich_bemat_thamC_mF9": 0.100},
    3: {"K_HE": 0.180, "K_FE_toi_cai_thien_mF6": 0.060,
        "K_FE_thuong_hoa_thamN_mF6": 0.060, "K_FE_toi_the_tich_bemat_thamC_mF9": 0.040},
    4: {"K_HE": 0.125, "K_FE_toi_cai_thien_mF6": 0.038,
        "K_FE_thuong_hoa_thamN_mF6": 0.038, "K_FE_toi_the_tich_bemat_thamC_mF9": 0.015},
    5: {"K_HE": 0.063, "K_FE_toi_cai_thien_mF6": 0.013,
        "K_FE_thuong_hoa_thamN_mF6": 0.013, "K_FE_toi_the_tich_bemat_thamC_mF9": 0.004},
}

STANDARD_MODULES = [1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0]

BANG_6_13_CON_THANG = {9: 1.5, 8: 4.0, 7: 8.0, 6: 12.0}

BANG_6_15 = {
    ("HB<=350", "thang_khong_vat"): (0.006, 0.016),
    ("HB<=350", "thang_co_vat"):    (0.004, 0.011),
    ("HB<=350", "nghieng"):          (0.002, 0.006),
    ("HB>350",  "thang_khong_vat"): (0.014, 0.016),
    ("HB>350",  "thang_co_vat"):    (0.010, 0.011),
    ("HB>350",  "nghieng"):          (0.004, 0.006),
}

BANG_6_16 = {
    6: {"<=3.55": 38, "3.55-10": 42, ">10": 48},
    7: {"<=3.55": 47, "3.55-10": 53, ">10": 64},
    8: {"<=3.55": 56, "3.55-10": 61, ">10": 73},
    9: {"<=3.55": 73, "3.55-10": 82, ">10": 100},
}

_YF_TABLE = {
    17:  4.26,
    20:  4.08,
    22:  4.00,
    25:  3.90,
    30:  3.80,
    40:  3.70,
    50:  3.65,
    60:  3.62,
    80:  3.61,
    100: 3.60,
    150: 3.60,
}

BANG_6_22 = {
    40:  {"thang": {1: 24, 2: 20, 3.15: 18, 4: 16, 6: 15},
          "nghieng": {1: 21, 2: 16, 3.15: 12, 4: 11, 6: 9}},
    60:  {"thang": {1: 24, 2: 20, 3.15: 18, 4: 16, 6: 15},
          "nghieng": {1: 21, 2: 16, 3.15: 13, 4: 12, 6: 10}},
    80:  {"thang": {1: 25, 2: 21, 3.15: 19, 4: 17, 6: 16},
          "nghieng": {1: 22, 2: 17, 3.15: 14, 4: 13, 6: 10}},
    100: {"thang": {1: 25, 2: 21, 3.15: 19, 4: 17, 6: 16},
          "nghieng": {1: 23, 2: 17, 3.15: 15, 4: 13, 6: 11}},
    125: {"thang": {1: 26, 2: 22, 3.15: 20, 4: 18, 6: 17},
          "nghieng": {1: 24, 2: 18, 3.15: 16, 4: 14, 6: 12}},
    160: {"thang": {1: 27, 2: 24, 3.15: 22, 4: 21, 6: 18},
          "nghieng": {1: 26, 2: 20, 3.15: 18, 4: 17, 6: 14}},
    200: {"thang": {1: 30, 2: 28, 3.15: 27, 4: 24, 6: 22},
          "nghieng": {1: 29, 2: 24, 3.15: 22, 4: 20, 6: 18}},
}

ZM_TABLE = {
    "thep_thep": 274, "thep_gang": 234, "thep_gang_dong": 225,
    "gang_gang": 209, "textolit_thep": 69.5, "poliamid_thep": 47.5,
}


# ─────────────────────────────────────────────────────────────────────────────
# DATACLASSES
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class VatLieu:
    ten: str
    nhiet_luyen: str
    do_ran: float
    don_vi_do_ran: str
    sigma_b: float
    sigma_ch: float
    la_banh_nho: bool = True

@dataclass
class ThongSoUngSuat:
    sigma_Hlim: float
    S_H: float
    sigma_Flim: float
    S_F: float
    N_HO: float
    N_FO: float = 4e6
    K_HL: float = 1.0
    K_FL: float = 1.0
    sigma_H_cp: float = 0.0
    sigma_F_cp: float = 0.0

@dataclass
class ThongSoHinhHoc:
    Z1: int
    Z2: int
    u_tt: float
    sai_so_u: float
    mte: float
    mtm: float
    Re: float
    b: float
    delta1_deg: float
    delta2_deg: float
    dm1: float
    dm2: float
    de1: float
    de2: float
    he: float
    hae: float
    hfe: float
    dae1: float
    dae2: float


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 1 – VẬT LIỆU VÀ ỨNG SUẤT CHO PHÉP
# ─────────────────────────────────────────────────────────────────────────────

def tinh_sigma_Hlim_Flim(vat_lieu):
    bang = BANG_6_2[vat_lieu.nhiet_luyen]
    do_ran = vat_lieu.do_ran
    return (bang["sigma_Hlim_func"](do_ran), bang["S_H"],
            bang["sigma_Flim_func"](do_ran), bang["S_F"])

def tinh_N_HO(HB):
    return 30.0 * (HB ** 2.4)

def tinh_NHE_tinh(c, n, t_h):
    return 60.0 * c * n * t_h

def tinh_NHE_thay_doi(c, Ti_list, Tmax, ni_list, ti_list):
    return 60.0 * c * sum((Ti/Tmax)**3 * ni * ti
                           for Ti, ni, ti in zip(Ti_list, ni_list, ti_list))

def tinh_NFE_thay_doi(c, Ti_list, Tmax, ni_list, ti_list, mF=6):
    return 60.0 * c * sum((Ti/Tmax)**mF * ni * ti
                           for Ti, ni, ti in zip(Ti_list, ni_list, ti_list))

def tinh_NHE_che_do(che_do, N_sigma, nhiet_luyen="thuong_hoa_toi_cai_thien"):
    data = BANG_6_4[che_do]
    K_HE = data["K_HE"]
    if nhiet_luyen in ("thuong_hoa_toi_cai_thien", "toi_cai_thien",
                        "thuong_hoa", "tham_nito_toi"):
        K_FE = data["K_FE_thuong_hoa_thamN_mF6"]
    else:
        K_FE = data["K_FE_toi_the_tich_bemat_thamC_mF9"]
    return round(K_HE * N_sigma, 0), round(K_FE * N_sigma, 0)

def tinh_K_HL(N_HO, N_HE, mH=6):
    return 1.0 if N_HE >= N_HO else (N_HO / N_HE) ** (1.0 / mH)

def tinh_K_FL(N_FO, N_FE, mF=6):
    return 1.0 if N_FE >= N_FO else (N_FO / N_FE) ** (1.0 / mF)

def tinh_ung_suat_cho_phep(vat_lieu, c, n, t_h, K_FC=1.0,
                            che_do_tai="tinh", Ti_list=None, Tmax=None,
                            ni_list=None, ti_list=None, che_do=0):
    sigma_Hlim, S_H, sigma_Flim, S_F = tinh_sigma_Hlim_Flim(vat_lieu)
    HB = vat_lieu.do_ran if vat_lieu.don_vi_do_ran == "HB" else None
    N_HO = tinh_N_HO(HB) if HB else 1e7
    N_FO = 4e6

    if che_do_tai == "tinh":
        N = tinh_NHE_tinh(c, n, t_h)
        NHE = NFE = N
    elif che_do_tai == "thay_doi":
        NHE = tinh_NHE_thay_doi(c, Ti_list, Tmax, ni_list, ti_list)
        mF = 6.0 if vat_lieu.nhiet_luyen == "thuong_hoa_toi_cai_thien" else 9.0
        NFE = tinh_NFE_thay_doi(c, Ti_list, Tmax, ni_list, ti_list, mF)
    else:
        N_sigma = tinh_NHE_tinh(c, n, t_h)
        NHE, NFE = tinh_NHE_che_do(che_do, N_sigma, vat_lieu.nhiet_luyen)

    mH = 6.0
    mF = 6.0 if vat_lieu.don_vi_do_ran == "HB" else 9.0
    K_HL = tinh_K_HL(N_HO, NHE, mH)
    K_FL = tinh_K_FL(N_FO, NFE, mF)

    return ThongSoUngSuat(
        sigma_Hlim=sigma_Hlim, S_H=S_H,
        sigma_Flim=sigma_Flim, S_F=S_F,
        N_HO=N_HO, N_FO=N_FO, K_HL=K_HL, K_FL=K_FL,
        sigma_H_cp=(sigma_Hlim / S_H) * K_HL,
        sigma_F_cp=(sigma_Flim / S_F) * K_FC * K_FL,
    )

def tinh_sigma_H_cp_truyen_dong(ts1, ts2, loai_rang="thang"):
    if loai_rang == "thang":
        return min(ts1.sigma_H_cp, ts2.sigma_H_cp)
    tb = (ts1.sigma_H_cp + ts2.sigma_H_cp) / 2.0
    return min(tb, 1.15 * min(ts1.sigma_H_cp, ts2.sigma_H_cp))

def tinh_sigma_qua_tai_cho_phep(vat_lieu):
    if vat_lieu.nhiet_luyen in ("thuong_hoa_toi_cai_thien", "toi_the_tich"):
        sigma_H_max_cp = 2.8 * vat_lieu.sigma_ch
    else:
        sigma_H_max_cp = 40.0 * vat_lieu.do_ran
    HB = vat_lieu.do_ran if vat_lieu.don_vi_do_ran == "HB" else None
    sigma_F_max_cp = (0.8 if HB and HB <= 350 else 0.6) * vat_lieu.sigma_ch
    return sigma_H_max_cp, sigma_F_max_cp


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 2 – THIẾT KẾ HÌNH HỌC
# ─────────────────────────────────────────────────────────────────────────────

def tinh_chieu_dai_con_ngoai_so_bo(T1, u, sigma_H_cp, K_Hbeta=1.18,
                                    K_be=0.3, K_d=100.0):
    K_R = 0.5 * K_d
    return K_R * math.sqrt(u**2 + 1) * (
        T1 * K_Hbeta / ((1 - K_be) * K_be * sigma_H_cp**2 * u)
    ) ** (1.0 / 3.0)

def chon_so_rang_banh_nho(u, de1_sb, loai_rang="thang"):
    de1_keys = sorted(BANG_6_22.keys())
    de1_key = de1_keys[-1]
    for k in de1_keys:
        if k >= de1_sb:
            de1_key = k
            break
    bang_con = BANG_6_22[de1_key].get(loai_rang, BANG_6_22[de1_key]["thang"])
    u_keys = sorted(bang_con.keys())
    u_key = u_keys[-1]
    for uk in u_keys:
        if uk >= u:
            u_key = uk
            break
    return math.ceil(1.6 * bang_con[u_key])

def tinh_modun_trung_binh_so_bo(Re, K_be, Z1, u):
    Z2 = round(u * Z1)
    dm1 = 2 * Re * (1 - 0.5 * K_be) * Z1 / math.sqrt(Z1**2 + Z2**2)
    return dm1 / Z1, dm1

def tinh_modun_ngoai(mtm, K_be):
    return mtm / (1.0 - 0.5 * K_be)

def chon_modun_tieu_chuan(mte_sb):
    for m in sorted(STANDARD_MODULES):
        if m >= mte_sb:
            return m
    return STANDARD_MODULES[-1]

def tinh_K_Hbeta_theo_psi_bd(psi_bd, HB_max=350):
    bang = [(0.2, 1.00), (0.4, 1.04), (0.6, 1.08), (0.8, 1.13),
            (1.0, 1.18), (1.2, 1.25), (1.4, 1.32)]
    if psi_bd <= bang[0][0]:  return bang[0][1]
    if psi_bd >= bang[-1][0]: return bang[-1][1]
    for i in range(len(bang) - 1):
        x0, y0 = bang[i]; x1, y1 = bang[i+1]
        if x0 <= psi_bd <= x1:
            return y0 + (y1 - y0) * (psi_bd - x0) / (x1 - x0)
    return 1.18

def tinh_K_Fbeta_bang_6_21(K_be, u, HB_max=350):
    """
    Tra K_Fbeta từ bảng 6.21 (Trịnh Chất) theo tham số x = K_be·u/(2-K_be).
    Dùng cột: Sơ đồ I, trục lắp trên ổ ĐŨA, loại răng 1;2 (thẳng/nghiêng).

    Lý do chọn cột này: K_Hbeta nội suy từ cùng cột → ≈ 1.18 (khớp case study).
    K_Fbeta KHÁC K_Hbeta — tra cột K_Fβ riêng, không dùng K_Hbeta thay thế.

    Bảng 6.21 – Sơ đồ I, ổ ĐŨA, loại 1;2, trích nguyên văn:
      HB ≤ 350* :  x→ [0.2→1.08, 0.4→1.15, 0.6→1.25, 0.8→1.35, 1.0→1.45]
      HB > 350  :  x→ [0.2→1.15, 0.4→1.30, 0.6→1.48, 0.8→1.67, 1.0→1.90]

    Đối chiếu: x=K_be·u/(2-K_be)=0.7941 → nội suy K_Fbeta≈1.347,
    làm tròn theo row x=0.8 → K_Fbeta=1.35. Case study dùng 1.35.
    """
    x = K_be * u / (2.0 - K_be)
    if HB_max <= 350:
        # Sơ đồ I, ổ đũa, HB≤350, loại 1;2 — đọc trực tiếp từ bảng 6.21
        bang = [(0.2, 1.08), (0.4, 1.15), (0.6, 1.25), (0.8, 1.35), (1.0, 1.45)]
    else:
        # Sơ đồ I, ổ đũa, HB>350, loại 1;2
        bang = [(0.2, 1.15), (0.4, 1.30), (0.6, 1.48), (0.8, 1.67), (1.0, 1.90)]
    if x <= bang[0][0]:  return bang[0][1]
    if x >= bang[-1][0]: return bang[-1][1]
    for i in range(len(bang) - 1):
        x0, y0 = bang[i]; x1, y1 = bang[i+1]
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return bang[-1][1]

def tinh_K_Hbeta_bang_6_21(K_be, u, HB_max=350):
    """
    Tra K_Hbeta từ bảng 6.21 cho bánh răng CÔN.
    Dùng cột: Sơ đồ I, trục lắp trên ổ ĐŨA, loại 1;2.
    Tham số: x = K_be·u / (2 - K_be).

    Bảng 6.21 – Sơ đồ I, ổ ĐŨA, loại 1;2:
      HB ≤ 350*: x→ [0.2→1.04, 0.4→1.08, 0.6→1.13, 0.8→1.18, 1.0→1.28]
      HB > 350 : x→ [0.2→1.08, 0.4→1.20, 0.6→1.32, 0.8→1.44, 1.0→  - ]

    Đối chiếu: x=0.7941 → nội suy K_Hbeta≈1.178 → làm tròn = 1.18 ✓
    """
    x = K_be * u / (2.0 - K_be)
    if HB_max <= 350:
        bang = [(0.2, 1.04), (0.4, 1.08), (0.6, 1.13), (0.8, 1.18), (1.0, 1.28)]
    else:
        bang = [(0.2, 1.08), (0.4, 1.20), (0.6, 1.32), (0.8, 1.44)]
    if x <= bang[0][0]:  return bang[0][1]
    if x >= bang[-1][0]: return bang[-1][1]
    for i in range(len(bang) - 1):
        x0, y0 = bang[i]; x1, y1 = bang[i+1]
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return bang[-1][1]


def kiem_tra_dieu_kien_hinh_hoc(gg, K_be, Z1_min=12):
    canh_bao = []
    b_Re = gg.b / gg.Re
    ok_b_Re = 0.25 <= b_Re <= 0.35
    if not ok_b_Re:
        canh_bao.append(
            f"   b/Re = {b_Re:.3f} nằm ngoài [0.25, 0.35] "
            f"(b={gg.b:.2f} mm, Re={gg.Re:.2f} mm)")
    eps_alpha = 1.88 - 3.2 * (1.0/gg.Z1 + 1.0/gg.Z2)
    ok_eps = eps_alpha >= 1.2
    if not ok_eps:
        canh_bao.append(f"   εα = {eps_alpha:.3f} < 1.2 — ăn khớp không liên tục")
    ok_Z1 = gg.Z1 >= Z1_min
    if not ok_Z1:
        canh_bao.append(f"   Z1 = {gg.Z1} < Z1_min = {Z1_min} — nguy cơ cắt chân răng")
    return {"ok_b_Re": ok_b_Re, "ok_eps": ok_eps, "ok_Z1_min": ok_Z1,
            "eps_alpha": eps_alpha, "b_Re": b_Re, "canh_bao": canh_bao,
            "tat_ca_dat": ok_b_Re and ok_eps and ok_Z1}

def tinh_thong_so_hinh_hoc(T1, u, sigma_H_cp, K_Hbeta=1.18, K_be=0.3,
                             K_d=100.0, Re_sb=None, vat_lieu_banh_nho_HB=250,
                             loai_rang="thang"):
    Re_sb = tinh_chieu_dai_con_ngoai_so_bo(T1, u, sigma_H_cp, K_Hbeta, K_be, K_d)
    de1_sb = 2.0 * Re_sb / math.sqrt(u**2 + 1)
    Z1 = chon_so_rang_banh_nho(u, de1_sb, loai_rang)
    Z2 = round(u * Z1)
    u_tt = Z2 / Z1
    mtm_sb, _ = tinh_modun_trung_binh_so_bo(Re_sb, K_be, Z1, u)
    mte_sb = tinh_modun_ngoai(mtm_sb, K_be)
    mte = chon_modun_tieu_chuan(mte_sb)
    mtm = mte * (1.0 - 0.5 * K_be)
    Re = 0.5 * mte * math.sqrt(Z1**2 + Z2**2)
    b = K_be * Re_sb  
    delta1 = math.atan(Z1 / Z2)
    delta2 = math.pi / 2 - delta1
    de1 = mte * Z1;  de2 = mte * Z2
    dm1 = mtm * Z1;  dm2 = (1 - 0.5 * K_be) * de2
    he  = 2.2 * mte;  hae = mte;  hfe = he - hae
    dae1 = de1 + 2.0 * hae * math.cos(delta1)
    dae2 = de2 + 2.0 * hae * math.cos(delta2)
    return ThongSoHinhHoc(
        Z1=Z1, Z2=Z2, u_tt=u_tt, sai_so_u=abs(u_tt-u)/u*100,
        mte=mte, mtm=mtm, Re=Re, b=b,
        delta1_deg=math.degrees(delta1), delta2_deg=math.degrees(delta2),
        dm1=dm1, dm2=dm2, de1=de1, de2=de2,
        he=he, hae=hae, hfe=hfe, dae1=dae1, dae2=dae2,
    )


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 3 – KIỂM NGHIỆM ĐỘ BỀN TIẾP XÚC
# ─────────────────────────────────────────────────────────────────────────────

def tra_cap_chinh_xac(v):
    for cap in sorted(BANG_6_13_CON_THANG.keys(), reverse=True):
        if v <= BANG_6_13_CON_THANG[cap]:
            return cap
    return 6

def tinh_van_toc_vong(dm1, n1):
    return math.pi * dm1 * n1 / 60000.0

def tra_delta_g0(HB1, HB2, dang_rang, cap_chinh_xac, mte):
    dieu_kien = "HB<=350" if (HB1 <= 350 and HB2 <= 350) else "HB>350"
    delta_H, delta_F = BANG_6_15.get((dieu_kien, dang_rang),
                                      BANG_6_15[("HB<=350", "thang_khong_vat")])
    bang_g0 = BANG_6_16[cap_chinh_xac]
    if mte <= 3.55:   g0 = bang_g0["<=3.55"]
    elif mte <= 10:   g0 = bang_g0["3.55-10"]
    else:             g0 = bang_g0[">10"]
    return delta_H, delta_F, g0

def tinh_Z_H(beta_deg=0.0, alpha_tw_deg=20.0):
    alpha_tw = math.radians(alpha_tw_deg)
    beta_b = math.atan(math.cos(alpha_tw) * math.tan(math.radians(beta_deg)))
    return math.sqrt(2.0 * math.cos(beta_b) / math.sin(2.0 * alpha_tw))

def tinh_eps_alpha(Z1, Z2, beta_deg=0.0):
    return (1.88 - 3.2 * (1.0/Z1 + 1.0/Z2)) * math.cos(math.radians(beta_deg))

def tinh_Z_eps(eps_alpha, eps_beta=0.0):
    if eps_beta == 0:     return math.sqrt((4.0 - eps_alpha) / 3.0)
    elif eps_beta < 1:    return math.sqrt((4.0-eps_alpha)*(1.0-eps_beta)/3.0 + eps_beta)
    else:                 return math.sqrt(1.0 / eps_alpha)

def kiem_nghiem_tiep_xuc(T1, u, n1, gg, sigma_H_cp, K_Hbeta=1.18,
                          HB1=250, HB2=240, ZM=274.0,
                          dang_rang="thang_khong_vat"):
    v = tinh_van_toc_vong(gg.dm1, n1)
    cap_cx = tra_cap_chinh_xac(v)
    K_Halpha = 1.0
    delta_H, _, g0 = tra_delta_g0(HB1, HB2, dang_rang, cap_cx, gg.mte)

    # ── BUG 2 FIX: CT 6.64 Trịnh Chất ──────────────────────────────
    vH = delta_H * g0 * v * math.sqrt(gg.dm1 * (u + 1) / u)
    # ─────────────────────────────────────────────────────────────────

    K_Hv = 1.0 + (vH * gg.b * gg.dm1) / (2.0 * T1 * K_Hbeta * K_Halpha)
    K_H = K_Hbeta * K_Halpha * K_Hv
    ZH = tinh_Z_H()
    eps_alpha = tinh_eps_alpha(gg.Z1, gg.Z2)
    Z_eps = tinh_Z_eps(eps_alpha)

    # ── BUG 3 FIX (lần 2): CT 6.58 Trịnh Chất – cấu trúc NESTED SQRT ──────
    nen = (2.0 * T1 * K_H * math.sqrt(u**2 + 1)) / (0.85 * gg.b * u * gg.dm1**2)
    # ─────────────────────────────────────────────────────────────────

    sigma_H = ZM * ZH * Z_eps * math.sqrt(nen)
    chenh = (sigma_H - sigma_H_cp) / sigma_H_cp * 100.0
    return {
        "v": v, "cap_cx": cap_cx, "vH": vH,
        "K_Hbeta": K_Hbeta, "K_Halpha": K_Halpha, "K_Hv": K_Hv, "K_H": K_H,
        "ZH": ZH, "eps_alpha": eps_alpha, "Z_eps": Z_eps,
        "ZM": ZM, "sigma_H": sigma_H, "sigma_H_cp": sigma_H_cp,
        "dat": sigma_H <= sigma_H_cp,
        "chenh_lech_phan_tram": chenh,
        "ghi_chu": "Đạt" if sigma_H <= sigma_H_cp
                   else f"Không đạt (vượt {chenh:.1f}%)" +
                        (" — chấp nhận nếu ≤4%" if chenh <= 4 else ""),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 4 – KIỂM NGHIỆM ĐỘ BỀN UỐN
# ─────────────────────────────────────────────────────────────────────────────

def tra_YF(z_tuong_duong, x=0.0):
    keys = sorted(_YF_TABLE.keys())
    if z_tuong_duong <= keys[0]:  return _YF_TABLE[keys[0]]
    if z_tuong_duong >= keys[-1]: return _YF_TABLE[keys[-1]]
    for i in range(len(keys) - 1):
        z0, z1 = keys[i], keys[i+1]
        if z0 <= z_tuong_duong <= z1:
            return _YF_TABLE[z0] + (_YF_TABLE[z1]-_YF_TABLE[z0])*(z_tuong_duong-z0)/(z1-z0)
    return _YF_TABLE[keys[-1]]

def kiem_nghiem_uon(T1, u, n1, gg, sigma_F1_cp, sigma_F2_cp,
                     K_Fbeta=1.18, HB1=250, HB2=240,
                     dang_rang="thang_khong_vat", x1=0.0, x2=0.0):
    """
    BUG 4 FIX (vF) + BUG 5 FIX (σF):

    BUG 4: CT 6.64 – vF phải dùng sqrt(dm1·(u+1)/u), không phải sqrt(dm1/u).

    BUG 5: CT 6.65 Trịnh Chất – công thức σF đúng:
        σF1 = 2·T1·KF·Yε·Yβ·YF1 / (0.85 · b · mtm · dm1)
    Code cũ dùng mte thay mtm và bỏ hệ số 0.85.
    """
    v = tinh_van_toc_vong(gg.dm1, n1)
    cap_cx = tra_cap_chinh_xac(v)
    K_Falpha = 1.0
    _, delta_F, g0 = tra_delta_g0(HB1, HB2, dang_rang, cap_cx, gg.mte)

    # ── BUG 4 FIX: CT 6.64 ──────────────────────────────────────────
    vF = delta_F * g0 * v * math.sqrt(gg.dm1 * (u + 1) / u)
    # ─────────────────────────────────────────────────────────────────

    K_Fv = 1.0 + (vF * gg.b * gg.dm1) / (2.0 * T1 * K_Fbeta * K_Falpha)
    K_F = K_Fbeta * K_Falpha * K_Fv
    eps_alpha = tinh_eps_alpha(gg.Z1, gg.Z2)
    Y_eps = 1.0 / eps_alpha
    Y_beta = 1.0
    YF1 = tra_YF(gg.Z1, x1)
    YF2 = tra_YF(gg.Z2, x2)

    # ── BUG 5 FIX: CT 6.65 ──────────────────────────────────────────
    sigma_F1 = (2.0 * T1 * K_F * Y_eps * Y_beta * YF1
                / (0.85 * gg.b * gg.mtm * gg.dm1))
    sigma_F2 = sigma_F1 * YF2 / YF1
    # ─────────────────────────────────────────────────────────────────

    return {
        "K_Fbeta": K_Fbeta, "K_Falpha": K_Falpha, "K_Fv": K_Fv, "K_F": K_F,
        "vF": vF,
        "eps_alpha": eps_alpha, "Y_eps": Y_eps,
        "YF1": YF1, "YF2": YF2,
        "sigma_F1": sigma_F1, "sigma_F1_cp": sigma_F1_cp,
        "dat_uon1": sigma_F1 <= sigma_F1_cp,
        "sigma_F2": sigma_F2, "sigma_F2_cp": sigma_F2_cp,
        "dat_uon2": sigma_F2 <= sigma_F2_cp,
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 5 – KIỂM NGHIỆM QUÁ TẢI
# ─────────────────────────────────────────────────────────────────────────────

def kiem_nghiem_qua_tai(sigma_H, sigma_F1, sigma_F2,
                         sigma_H_max_cp1, sigma_H_max_cp2,
                         sigma_F1_max_cp, sigma_F2_max_cp, K_qt):
    sigma_H_max_cp = min(sigma_H_max_cp1, sigma_H_max_cp2)
    sqrt_Kqt = math.sqrt(K_qt)
    return {
        "K_qt": K_qt,
        "sigma_H_max":    sigma_H  * math.sqrt(K_qt),
        "sigma_H_max_cp": sigma_H_max_cp,
        "dat_H_max":      sigma_H  * math.sqrt(K_qt) <= sigma_H_max_cp,
        "sigma_F1_max":   sigma_F1 * math.sqrt(K_qt),
        "sigma_F1_max_cp": sigma_F1_max_cp,
        "dat_F1_max":     sigma_F1 * K_qt <= sigma_F1_max_cp,
        "sigma_F2_max":   sigma_F2 * math.sqrt(K_qt),
        "sigma_F2_max_cp": sigma_F2_max_cp,
        "dat_F2_max":     sigma_F2 * K_qt <= sigma_F2_max_cp,
    }


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 6 – BẢNG THÔNG SỐ TỔNG HỢP
# ─────────────────────────────────────────────────────────────────────────────

def in_bang_thong_so(gg: ThongSoHinhHoc, u_yc: float):
    SEP = "=" * 65
    print(f"\n{SEP}")
    print("  BẢNG THÔNG SỐ VÀ KÍCH THƯỚC BỘ TRUYỀN BÁNH RĂNG CÔN")
    print(SEP)
    print(f"  {'Thông số':<40} {'Giá trị':>10}  {'Đơn vị'}")
    print("  " + "-" * 60)

    rows = [
        ("Chiều dài côn ngoài Re",               f"{gg.Re:.3f}",    "mm"),
        ("Môđun mặt đầu ngoài mte",              f"{gg.mte:.4f}",   "mm"),
        ("Môđun trung bình mtm",                 f"{gg.mtm:.4f}",   "mm"),
        ("Chiều rộng vành răng b",               f"{gg.b:.3f}",     "mm"),
        ("Tỉ số truyền yêu cầu u",               f"{u_yc:.4f}",     "—"),
        ("Tỉ số truyền thực u_tt",               f"{gg.u_tt:.4f}",  "—"),
        ("Sai số tỉ số truyền Δu",               f"{gg.sai_so_u:.2f}", "%"),
        ("Số răng bánh nhỏ Z₁",                  f"{gg.Z1}",        "răng"),
        ("Số răng bánh lớn Z₂",                  f"{gg.Z2}",        "răng"),
        ("Đường kính ngoài bánh nhỏ de1",        f"{gg.de1:.3f}",   "mm"),
        ("Đường kính ngoài bánh lớn de2",        f"{gg.de2:.3f}",   "mm"),
        ("Góc côn chia bánh nhỏ δ₁",             f"{gg.delta1_deg:.3f}", "°"),
        ("Góc côn chia bánh lớn δ₂",             f"{gg.delta2_deg:.3f}", "°"),
        ("Chiều cao răng ngoài he",              f"{gg.he:.4f}",    "mm"),
        ("Chiều cao đầu răng ngoài hae",         f"{gg.hae:.4f}",   "mm"),
        ("Chiều cao chân răng ngoài hfe",        f"{gg.hfe:.4f}",   "mm"),
        ("Đường kính trung bình bánh nhỏ dm1",   f"{gg.dm1:.4f}",   "mm"),
        ("Đường kính trung bình bánh lớn dm2",   f"{gg.dm2:.4f}",   "mm"),
        ("Đường kính đỉnh răng ngoài bánh nhỏ dae1", f"{gg.dae1:.3f}", "mm"),
        ("Đường kính đỉnh răng ngoài bánh lớn dae2", f"{gg.dae2:.3f}", "mm"),
    ]
    for name, val, unit in rows:
        print(f"  {name:<40} {val:>10}  {unit}")
    print(SEP)


# ─────────────────────────────────────────────────────────────────────────────
# MODULE 7 – HÀM TỔNG HỢP THIẾT KẾ HOÀN CHỈNH
# ─────────────────────────────────────────────────────────────────────────────

def thiet_ke_banh_rang_con(
    T1: float, n1: float, u: float, t_h: float,
    vat_lieu_1: VatLieu, vat_lieu_2: VatLieu,
    K_be: float = 0.3,
    K_Hbeta: float = None,
    K_Fbeta: float = None,
    K_FC: float = 1.0,
    K_qt: float = 2.2,        # ← BUG 6 FIX: đổi default 1.4 → 2.2
    c: int = 1,
    ZM: float = 274.0,
    loai_rang: str = "thang",
    in_ket_qua: bool = True,
) -> dict:
    """
    Hàm thiết kế hoàn chỉnh bộ truyền bánh răng côn – răng thẳng.

    BUG 1 FIX: b = K_be * Re_sb (cố định, không thay đổi khi tăng mte).
    BUG 2 FIX: vH dùng sqrt(dm1*(u+1)/u) – CT 6.64.
    BUG 3 FIX: CT 6.58 nested sqrt: nen = 2*T1*KH*sqrt(u²+1)/(0.85*b*u*dm1²).
    BUG 4 FIX: vF dùng sqrt(dm1*(u+1)/u) – CT 6.68a.
    BUG 5 FIX: σF dùng CT 6.65 với mtm và hệ số 0.85.
    BUG 6 FIX: K_qt mặc định = 2.2.
    BUG 7 FIX: K_Fbeta tra bảng 6.21 theo x=K_be·u/(2-K_be), KHÔNG dùng K_Hbeta.
    BUG 8 FIX: n1 phải là tốc độ trục VÀO bánh côn nhỏ (không phải n_motor).
    """
    SEP = "=" * 65
    MAX_ITER = len(STANDARD_MODULES)

    def pr(text=""):
        if in_ket_qua: print(text)

    pr(SEP)
    pr("  THIẾT KẾ BỘ TRUYỀN BÁNH RĂNG CÔN – RĂNG THẲNG")
    pr(SEP)

    # ── BƯỚC 1: Ứng suất cho phép ─────────────────────────────────────
    pr("\n▌ BƯỚC 1: ỨNG SUẤT CHO PHÉP")
    pr("-" * 45)
    ts1 = tinh_ung_suat_cho_phep(vat_lieu_1, c, n1, t_h, K_FC)
    ts2 = tinh_ung_suat_cho_phep(vat_lieu_2, c, n1/u, t_h, K_FC)
    sigma_H_cp = tinh_sigma_H_cp_truyen_dong(ts1, ts2, loai_rang)
    sH_max_cp1, sF_max_cp1 = tinh_sigma_qua_tai_cho_phep(vat_lieu_1)
    sH_max_cp2, sF_max_cp2 = tinh_sigma_qua_tai_cho_phep(vat_lieu_2)

    pr(f"  Bánh nhỏ (1):  σ_Hlim={ts1.sigma_Hlim:.1f} MPa  |  σ_Flim={ts1.sigma_Flim:.1f} MPa")
    pr(f"                 K_HL={ts1.K_HL:.4f}  |  K_FL={ts1.K_FL:.4f}")
    pr(f"                 [σH]₁={ts1.sigma_H_cp:.2f} MPa  |  [σF]₁={ts1.sigma_F_cp:.2f} MPa")
    pr(f"  Bánh lớn (2):  σ_Hlim={ts2.sigma_Hlim:.1f} MPa  |  σ_Flim={ts2.sigma_Flim:.1f} MPa")
    pr(f"                 K_HL={ts2.K_HL:.4f}  |  K_FL={ts2.K_FL:.4f}")
    pr(f"                 [σH]₂={ts2.sigma_H_cp:.2f} MPa  |  [σF]₂={ts2.sigma_F_cp:.2f} MPa")
    pr(f"  ⇒ [σH] bộ truyền = {sigma_H_cp:.2f} MPa  (lấy min)")

    # ── BƯỚC 2: Chiều dài côn ngoài sơ bộ ────────────────────────────
    pr("\n▌ BƯỚC 2: CHIỀU DÀI CÔN NGOÀI SƠ BỘ")
    pr("-" * 45)
    HB1 = vat_lieu_1.do_ran if vat_lieu_1.don_vi_do_ran == "HB" else 300
    HB2 = vat_lieu_2.do_ran if vat_lieu_2.don_vi_do_ran == "HB" else 300

    # K_Hbeta tra bảng 6.21 (sơ đồ I, ổ đũa) hoặc dùng giá trị nhập vào
    if K_Hbeta is None:
        K_Hbeta_sb = tinh_K_Hbeta_bang_6_21(K_be, u, HB_max=max(HB1, HB2))
        x_tra = K_be * u / (2.0 - K_be)
        pr(f"  K_Hβ tra bảng 6.21 (sơ đồ I, ổ đũa, HB≤350, loại 1;2):")
        pr(f"    x = K_be·u/(2-K_be) = {K_be}×{u}/(2-{K_be}) = {x_tra:.4f}")
        pr(f"    K_Hβ = {K_Hbeta_sb:.4f}  (nội suy, làm tròn → {round(K_Hbeta_sb,2)})")
    else:
        K_Hbeta_sb = K_Hbeta
        pr(f"  K_Hβ = {K_Hbeta_sb:.4f}  (nhập từ ngoài)")

    Re_sb = tinh_chieu_dai_con_ngoai_so_bo(T1, u, sigma_H_cp, K_Hbeta_sb, K_be)
    # BUG 1 FIX: b_fixed luôn dùng Re_sb ban đầu, không đổi theo mte
    b_fixed = K_be * Re_sb
    pr(f"  Re_sơ_bộ = {Re_sb:.3f} mm")
    pr(f"  b = K_be × Re_sb = {K_be} × {Re_sb:.3f} = {b_fixed:.3f} mm  (cố định)")

    # ── BƯỚC 3: Thông số ăn khớp & hình học ──────────────────────────
    pr("\n▌ BƯỚC 3: THÔNG SỐ ĂN KHỚP & HÌNH HỌC")
    pr("-" * 45)

    gg = tinh_thong_so_hinh_hoc(T1, u, sigma_H_cp, K_Hbeta_sb, K_be,
                                  vat_lieu_banh_nho_HB=HB1, loai_rang=loai_rang,
                                  Re_sb=Re_sb)
    # Gán b_fixed vào gg (đảm bảo b không bị ghi đè)
    gg = ThongSoHinhHoc(
        Z1=gg.Z1, Z2=gg.Z2, u_tt=gg.u_tt, sai_so_u=gg.sai_so_u,
        mte=gg.mte, mtm=gg.mtm, Re=gg.Re, b=b_fixed,
        delta1_deg=gg.delta1_deg, delta2_deg=gg.delta2_deg,
        dm1=gg.dm1, dm2=gg.dm2, de1=gg.de1, de2=gg.de2,
        he=gg.he, hae=gg.hae, hfe=gg.hfe, dae1=gg.dae1, dae2=gg.dae2,
    )

    # K_Hbeta dùng trong kiểm nghiệm = giá trị đã tra bảng 6.21 ở bước 2
    K_Hbeta_dung = K_Hbeta_sb

    # K_Fbeta tra bảng 6.21 riêng (cột K_Fβ, KHÔNG dùng K_Hbeta)
    K_Fbeta_dung = (K_Fbeta if K_Fbeta is not None
                    else tinh_K_Fbeta_bang_6_21(K_be, u, max(HB1, HB2)))
    x_tra = K_be * u / (2.0 - K_be)
    pr(f"  K_Fβ tra bảng 6.21 (cột K_Fβ, ổ đũa, HB≤350):")
    pr(f"    x = {x_tra:.4f}  →  K_Fβ = {K_Fbeta_dung:.4f}")

    dk_hh = kiem_tra_dieu_kien_hinh_hoc(gg, K_be)
    if dk_hh["canh_bao"]:
        pr("  ── Kiểm tra điều kiện hình học:")
        for cw in dk_hh["canh_bao"]: pr(cw)
    else:
        pr(f"  ✓ Điều kiện hình học: b/Re={dk_hh['b_Re']:.3f}∈[0.25,0.35], "
           f"εα={dk_hh['eps_alpha']:.3f}≥1.2, Z1≥12")

    pr(f"  Z₁={gg.Z1}  Z₂={gg.Z2}  u_tt={gg.u_tt:.4f}  Δu={gg.sai_so_u:.2f}%")
    pr(f"  mte={gg.mte} mm  mtm={gg.mtm:.4f} mm")
    pr(f"  Re={gg.Re:.3f} mm  b={gg.b:.3f} mm")
    pr(f"  δ₁={gg.delta1_deg:.3f}°  δ₂={gg.delta2_deg:.3f}°")
    pr(f"  dm1={gg.dm1:.3f} mm  dm2={gg.dm2:.3f} mm")
    pr(f"  de1={gg.de1:.3f} mm  de2={gg.de2:.3f} mm")
    pr(f"  he={gg.he:.4f} mm  hae={gg.hae:.4f} mm  hfe={gg.hfe:.4f} mm")
    pr(f"  dae1={gg.dae1:.3f} mm  dae2={gg.dae2:.3f} mm")

    # ── BƯỚC 4: Kiểm nghiệm tiếp xúc (vòng lặp tăng module) ──────────
    pr("\n▌ BƯỚC 4: KIỂM NGHIỆM ĐỘ BỀN TIẾP XÚC")
    pr("-" * 45)

    vong_lap = 0
    mte_thu = gg.mte

    while True:
        kn_tx = kiem_nghiem_tiep_xuc(T1, u, n1, gg, sigma_H_cp,
                                      K_Hbeta_dung, HB1, HB2, ZM,
                                      dang_rang="thang_khong_vat")
        chenh = kn_tx["chenh_lech_phan_tram"]
        if kn_tx["dat"] or chenh <= 4.0:
            break

        idx = STANDARD_MODULES.index(mte_thu) if mte_thu in STANDARD_MODULES else -1
        if idx == -1 or idx >= len(STANDARD_MODULES) - 1:
            pr("  Đã thử tất cả module tiêu chuẩn, σH vẫn vượt [σH].")
            break

        mte_moi = STANDARD_MODULES[idx + 1]
        pr(f"  σH vượt [σH] {chenh:.1f}% > 4% → tăng mte: {mte_thu} → {mte_moi} mm")
        mte_thu = mte_moi
        vong_lap += 1

        # BUG 1 FIX: b không thay đổi khi tăng module
        mtm_moi = mte_moi * (1.0 - 0.5 * K_be)
        Re_moi  = 0.5 * mte_moi * math.sqrt(gg.Z1**2 + gg.Z2**2)
        dm1_moi = mtm_moi * gg.Z1
        dm2_moi = (1 - 0.5 * K_be) * mte_moi * gg.Z2
        de1_moi = mte_moi * gg.Z1;  de2_moi = mte_moi * gg.Z2
        he_moi  = 2.2 * mte_moi;  hae_moi = mte_moi;  hfe_moi = he_moi - hae_moi
        d1r = math.radians(gg.delta1_deg);  d2r = math.radians(gg.delta2_deg)
        dae1_moi = de1_moi + 2.0 * hae_moi * math.cos(d1r)
        dae2_moi = de2_moi + 2.0 * hae_moi * math.cos(d2r)
        gg = ThongSoHinhHoc(
            Z1=gg.Z1, Z2=gg.Z2, u_tt=gg.u_tt, sai_so_u=gg.sai_so_u,
            mte=mte_moi, mtm=mtm_moi, Re=Re_moi, b=b_fixed,  # ← b_fixed
            delta1_deg=gg.delta1_deg, delta2_deg=gg.delta2_deg,
            dm1=dm1_moi, dm2=dm2_moi, de1=de1_moi, de2=de2_moi,
            he=he_moi, hae=hae_moi, hfe=hfe_moi, dae1=dae1_moi, dae2=dae2_moi,
        )
        if vong_lap >= MAX_ITER:
            pr("  Đã đạt giới hạn vòng lặp module.")
            break

    if vong_lap > 0:
        pr(f"  (Đã điều chỉnh module sau {vong_lap} vòng lặp → mte = {gg.mte} mm)")

    pr(f"  v={kn_tx['v']:.3f} m/s  →  Cấp chính xác: {kn_tx['cap_cx']}")
    pr(f"  vH={kn_tx['vH']:.4f}")
    pr(f"  ZH={kn_tx['ZH']:.4f}  εα={kn_tx['eps_alpha']:.4f}  Zε={kn_tx['Z_eps']:.4f}")
    pr(f"  KHβ={kn_tx['K_Hbeta']:.4f}  KHα={kn_tx['K_Halpha']:.4f}  KHv={kn_tx['K_Hv']:.4f}")
    pr(f"  KH={kn_tx['K_H']:.4f}")
    pr(f"  σH = {kn_tx['sigma_H']:.3f} MPa  ≤  [σH] = {sigma_H_cp:.3f} MPa ?")
    pr(f"  → {kn_tx['ghi_chu']}")

    # ── BƯỚC 5: Kiểm nghiệm uốn ──────────────────────────────────────
    pr("\n▌ BƯỚC 5: KIỂM NGHIỆM ĐỘ BỀN UỐN")
    pr("-" * 45)
    kn_uon = kiem_nghiem_uon(T1, u, n1, gg,
                              ts1.sigma_F_cp, ts2.sigma_F_cp,
                              K_Fbeta_dung, HB1, HB2)
    pr(f"  vF={kn_uon['vF']:.4f}")
    pr(f"  εα={kn_uon['eps_alpha']:.4f}  Yε={kn_uon['Y_eps']:.4f}")
    pr(f"  YF1={kn_uon['YF1']:.4f}  YF2={kn_uon['YF2']:.4f}")
    pr(f"  KFβ={kn_uon['K_Fbeta']:.4f}  KFα={kn_uon['K_Falpha']:.4f}  KFv={kn_uon['K_Fv']:.4f}")
    pr(f"  KF={kn_uon['K_F']:.4f}")
    pr(f"  σF1={kn_uon['sigma_F1']:.3f} MPa  ≤  [σF]₁={ts1.sigma_F_cp:.3f} MPa ?  "
       f"→ {'✓ Đạt' if kn_uon['dat_uon1'] else '✗ Không đạt'}")
    pr(f"  σF2={kn_uon['sigma_F2']:.3f} MPa  ≤  [σF]₂={ts2.sigma_F_cp:.3f} MPa ?  "
       f"→ {'✓ Đạt' if kn_uon['dat_uon2'] else '✗ Không đạt'}")

    # ── BƯỚC 6: Kiểm nghiệm quá tải ──────────────────────────────────
    pr("\n▌ BƯỚC 6: KIỂM NGHIỆM QUÁ TẢI")
    pr("-" * 45)
    kn_qt = kiem_nghiem_qua_tai(
        kn_tx["sigma_H"], kn_uon["sigma_F1"], kn_uon["sigma_F2"],
        sH_max_cp1, sH_max_cp2, sF_max_cp1, sF_max_cp2, K_qt
    )
    pr(f"  Kqt = {K_qt}")
    pr(f"  σH_max  = {kn_qt['sigma_H_max']:.3f}  ≤  [σH]max  = {kn_qt['sigma_H_max_cp']:.3f} ?  "
       f"→ {'Đạt' if kn_qt['dat_H_max'] else 'Không đạt'}")
    pr(f"  σF1_max = {kn_qt['sigma_F1_max']:.3f}  ≤  [σF1]max = {kn_qt['sigma_F1_max_cp']:.3f} ?  "
       f"→ {'Đạt' if kn_qt['dat_F1_max'] else 'Không đạt'}")
    pr(f"  σF2_max = {kn_qt['sigma_F2_max']:.3f}  ≤  [σF2]max = {kn_qt['sigma_F2_max_cp']:.3f} ?  "
       f"→ {'Đạt' if kn_qt['dat_F2_max'] else 'Không đạt'}")

    # ── BẢNG THÔNG SỐ TỔNG HỢP ───────────────────────────────────────
    if in_ket_qua:
        in_bang_thong_so(gg, u)

    return {
        "hinh_hoc": gg,
        "ts1": ts1, "ts2": ts2,
        "sigma_H_cp": sigma_H_cp,
        "K_Hbeta": K_Hbeta_dung,
        "K_Fbeta": K_Fbeta_dung,
        "b_fixed": b_fixed,
        "kiem_nghiem_tiep_xuc": kn_tx,
        "kiem_nghiem_uon": kn_uon,
        "kiem_nghiem_qua_tai": kn_qt,
        "kiem_tra_hinh_hoc": dk_hh,
        "dat_tat_ca": (kn_tx["dat"] and kn_uon["dat_uon1"] and kn_uon["dat_uon2"]
                       and kn_qt["dat_H_max"] and kn_qt["dat_F1_max"]
                       and kn_qt["dat_F2_max"]),
    }


# ─────────────────────────────────────────────────────────────────────────────
# MAIN – Case study kiểm tra
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    vat_lieu_banh_nho = VatLieu(
        ten="Thép C45",
        nhiet_luyen="thuong_hoa_toi_cai_thien",
        do_ran=250.0,
        don_vi_do_ran="HB",
        sigma_b=850.0,
        sigma_ch=580.0,
        la_banh_nho=True,
    )
    vat_lieu_banh_lon = VatLieu(
        ten="Thép C45",
        nhiet_luyen="thuong_hoa_toi_cai_thien",
        do_ran=240.0,
        don_vi_do_ran="HB",
        sigma_b=750.0,
        sigma_ch=450.0,
        la_banh_nho=False,
    )

    ket_qua = thiet_ke_banh_rang_con(
        T1         = 47980.997,
        # n1 = tốc độ trục VÀO bánh côn nhỏ (sau bộ truyền đai).
        # BUG 8: KHÔNG dùng tốc độ động cơ. Ví dụ: n_motor=980, u_dai→ n1=1168.8 rpm.
        n1         = 1168.8,
        u          = 4.5,
        t_h        = 17280.0,
        vat_lieu_1 = vat_lieu_banh_nho,
        vat_lieu_2 = vat_lieu_banh_lon,
        K_be       = 0.3,
        # K_Hbeta=None → tự tra bảng 6.21 (sơ đồ I, ổ đũa, HB≤350, loại 1;2)
        # K_Fbeta=None → tự tra bảng 6.21 (cột K_Fβ, sơ đồ I, ổ đũa)
        K_Hbeta    = None,
        K_Fbeta    = None,
        K_FC       = 1.0,
        K_qt       = 2.2,
        c          = 1,
        ZM         = 274.0,
        loai_rang  = "thang",
        in_ket_qua = True,
    )