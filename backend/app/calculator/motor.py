def tinh_HieuSuat_Tong(
    hieu_suat_dai=0.96, 
    hieu_suat_con=0.97, 
    hieu_suat_tru=0.98, 
    hieu_suat_o_lan=0.995, 
    hieu_suat_khop_noi=0.99):
    """
    Tính hiệu suất truyền động 
    Hệ thống: 1 đai, 1 cặp bánh răng côn, 1 cặp bánh răng trụ, 4 cặp ổ lăn, 1 khớp nối.
    """
    eta_total = hieu_suat_dai * hieu_suat_con * hieu_suat_tru * (hieu_suat_o_lan**4) * hieu_suat_khop_noi
    return round(eta_total, 3)

def tinh_P_can_thiet(P_tai, eta_total, K=1.0):
    """Tính công suất cần thiết Pct (kW)"""
    return (P_tai / 1000) * K / eta_total

def tinh_n_so_bo(n_iv, u_dai_sb=4, u_hgt_sb=10):
    """
    n_iv: số vòng quay của trục máy công tác INPUT USER (v/ph)
    u_dai_sb: Tỉ số truyền sơ bộ bộ truyền đai =4 (Dựa vào bảng 2.4 tỉ số truyền)
    u_hgt_sb: Tỉ số truyền sơ bộ HGT 2 cấp =10 
    """
    u_t_sb = u_dai_sb * u_hgt_sb
    n_sb = n_iv * u_t_sb
    return n_sb, u_t_sb

def query_dong_co(cursor, p_ct, n_sb):
    """
    p_ct: Công suất cần thiết (kW)
    n_sb: Tốc độ sơ bộ (v/ph)
    """
    # Logic: Chọn những động cơ có P >= P_ct
    # Sau đó sắp xếp theo:
    # 1. P tăng dần (để lấy cái tiết kiệm nhất)
    # 2. Độ chênh lệch n_dc so với n_sb ít nhất
    query = """
        SELECT *, ABS(TocDo_vph - %s) as diff_n
        FROM Thu_Vien_Dong_Co
        WHERE CongSuat_kW >= %s
        ORDER BY CongSuat_kW ASC, diff_n ASC
        LIMIT 3
    """
    cursor.execute(query, (n_sb, p_ct))
    options = cursor.fetchall()
    return options

def kiem_nghiem_qua_tai(dong_co_row, k_qt=1.5):
    """
    dong_co_row: Dòng dữ liệu động cơ lấy từ DB (dictionary)
    k_qt: Hệ số quá tải (Tmm/T). Với tải va đập nhẹ, thường lấy 1.2 - 1.5
    """
    # Lấy giá trị Tk/Tdn từ Database
    tk_tdn_dong_co = dong_co_row['Tk_Tdn']
    
    # Kiểm tra điều kiện 2.6
    if tk_tdn_dong_co >= k_qt:
        status = True
        message = f"Thỏa mãn điều kiện khởi động: {tk_tdn_dong_co} >= {k_qt}"
    else:
        status = False
        message = f"KHÔNG thỏa mãn: Mô-men khởi động động cơ ({tk_tdn_dong_co}) nhỏ hơn yêu cầu ({k_qt})"
    
    return status, message
def tinh_toan_he_thong_thuc_te(dc_chon, n_iv, u_dai_so_bo=2.5, u_con_so_bo=4.5):
    """
    dc_chon: Dictionary chứa thông tin động cơ người dùng đã chọn từ list options
    n_iv: Tốc độ trục công tác (70 v/ph)
    """
    n_dc_thuc = dc_chon['TocDo_vph']
    
    # 1. Tính tỷ số truyền tổng thực tế
    u_t_thuc = n_dc_thuc / n_iv
    
    # 2. Phân phối tỷ số truyền
    u_dai = u_dai_so_bo
    u_h = u_t_thuc / u_dai
    
    # Cấp nhanh (côn) và Cấp chậm (trụ)
    u_1 = u_con_so_bo
    u_2 = u_h / u_1
    
    return {
        "model": dc_chon['Model'],
        "u_t": round(u_t_thuc, 4),
        "u_dai": round(u_dai, 4),
        "u_1": round(u_1, 4),
        "u_2": round(u_2, 4)
    }
def tinh_thong_so_truc(P_dc, n_dc, u_list, eta_list):
    """
    u_list: [u_dai, u_con, u_tru]
    eta_list: [eta_dai, eta_con, eta_tru, eta_ol, eta_kn]
    """
    # 2.3.1 Tính Tốc độ quay (n)
    n1 = n_dc / u_list[0]
    n2 = n1 / u_list[1]
    n3 = n2 / u_list[2]
    
    # 2.3.2 Tính Công suất (P) - Tính ngược từ động cơ xuống
    P1 = P_dc * eta_list['dai'] * eta_list['o_lan']
    P2 = P1 * eta_list['con'] * eta_list['o_lan']
    P3 = P2 * eta_list['tru'] * eta_list['o_lan']
    # 2.3.3 Tính Moment xoắn (T) - Đơn vị N.mm
    # Công thức: T = 9.55 * 10^6 * (P / n)
    T_dc = 9.55 * 1e6 * (P_dc / n_dc)
    T1 = 9.55 * 1e6 * (P1 / n1)
    T2 = 9.55 * 1e6 * (P2 / n2)
    T3 = 9.55 * 1e6 * (P3 / n3)
    
    return {
        "truc_dc": {"P": P_dc, "n": n_dc, "T": T_dc},
        "truc_1":  {"P": P1, "n": n1, "T": T1},
        "truc_2":  {"P": P2, "n": n2, "T": T2},
        "truc_3":  {"P": P3, "n": n3, "T": T3}
    }

def kiem_nghiem_khoi_dong(dc_row, k_qt=1.3):
    """
    dc_row: Dictionary dữ liệu động cơ (có cột 'Tk_Tdn')
    k_qt: Hệ số quá tải khi khởi động (Tmm/T). 
          Với tải va đập nhẹ, thường chọn trong khoảng 1.2 - 1.5.
    """
    # Hệ số khởi động của động cơ từ Database (Tk/Tdn)
    h_so_dc = dc_row['Tk_Tdn']
    
    # Điều kiện kiểm nghiệm (Biểu thức 2.6): Tk/Tdn >= Tmm/T
    if h_so_dc >= k_qt:
        return True, f"Đạt (Tk/Tdn = {h_so_dc} >= Kqt = {k_qt})"
    else:
        return False, f"Không đạt (Tk/Tdn = {h_so_dc} < Kqt = {k_qt})"

def luu_ket_qua_final(cursor, id_duan, dc_chon, kq_u, kq_truc):
    sql = """
    INSERT INTO Ket_Qua_Chung (
        ID_DuAn, Model_DongCo, ut_thuc, u_dai, u1_con, u2_tru,
        P_dc, n_dc, T_dc, P1, n1, T1, P2, n2, T2, P3, n3, T3
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    values = (
        id_duan, dc_chon['Model'], kq_u['u_t'], kq_u['u_dai'], kq_u['u_1'], kq_u['u_2'],
        kq_truc['truc_dc']['P'], kq_truc['truc_dc']['n'], kq_truc['truc_dc']['T'],
        kq_truc['truc_1']['P'], kq_truc['truc_1']['n'], kq_truc['truc_1']['T'],
        kq_truc['truc_2']['P'], kq_truc['truc_2']['n'], kq_truc['truc_2']['T'],
        kq_truc['truc_3']['P'], kq_truc['truc_3']['n'], kq_truc['truc_3']['T']
    )
    cursor.execute(sql, values)