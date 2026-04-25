CREATE DATABASE IF NOT EXISTS dadn;
USE dadn;

-- ==========================================
-- I. THƯ VIỆN KỸ THUẬT (Giữ nguyên tên để code cũ chạy được)
-- ==========================================

-- 1. Thư viện Động cơ (Code cũ gọi là Thu_Vien_Dong_Co)
CREATE TABLE Thu_Vien_Dong_Co (
    ID_DongCo INT PRIMARY KEY AUTO_INCREMENT,
    Model VARCHAR(50) NOT NULL UNIQUE,
    CongSuat_kW FLOAT NOT NULL,  -- P_rated
    VanToc_vph INT NOT NULL,    -- n_rated
    HieuSuat FLOAT,
    CosPhi FLOAT,
    Tmax_Tdn FLOAT,
    Tk_Tdn FLOAT
);

-- 2. Thư viện Ổ lăn (Bổ sung mới)
CREATE TABLE Thu_Vien_O_Lan (
    ID_OLan INT PRIMARY KEY AUTO_INCREMENT,
    KyHieu VARCHAR(20) UNIQUE,
    d_trong FLOAT,
    D_ngoai FLOAT,
    B_rong FLOAT,
    C_dong FLOAT,
    C0_tinh FLOAT
);

-- 3. Thư viện Vật liệu
CREATE TABLE Vat_Lieu_Banh_Rang (
    ID_VatLieu INT PRIMARY KEY AUTO_INCREMENT,
    TenVatLieu VARCHAR(100) NOT NULL,
    DoRan_HB INT,
    Sigma_b FLOAT,
    Sigma_ch FLOAT
);

-- ==========================================
-- II. QUẢN LÝ DỰ ÁN & TÀI KHOẢN
-- ==========================================

CREATE TABLE Users (
    ID_User INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    FullName VARCHAR(100)
);

-- Tách bảng Dự án thành: Metadata và Inputs
CREATE TABLE Du_An (
    ID_DuAn INT PRIMARY KEY AUTO_INCREMENT,
    ID_User INT,
    TenDuAn VARCHAR(255),
    NgayTao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    BuocHienTai VARCHAR(20) DEFAULT 'M1',
    FOREIGN KEY (ID_User) REFERENCES Users(ID_User)
);

-- Lưu thông số đầu vào riêng biệt (Mấu chốt để re-calculate)
CREATE TABLE Du_An_Inputs (
    ID_DuAn INT PRIMARY KEY,
    P_working_kW FLOAT NOT NULL,
    n_working_vph FLOAT NOT NULL,
    Lh_hours INT,
    DacTinhTai VARCHAR(50),
    FOREIGN KEY (ID_DuAn) REFERENCES Du_An(ID_DuAn) ON DELETE CASCADE
);

-- ==========================================
-- III. KẾT QUẢ TÍNH TOÁN (M1 - M4)
-- ==========================================

-- Result_M1_Kinematics đã được GỘP vào M1_Checkpoint (xem phía dưới)
-- M1_Checkpoint vừa là debug log, vừa là kết quả chính thức của M1

-- Thông số các trục (I, II, III)
CREATE TABLE Thong_So_Cac_Truc (
    ID_Truc_Result INT PRIMARY KEY AUTO_INCREMENT,
    ID_DuAn INT,
    Ten_Truc VARCHAR(10),
    CongSuat_P FLOAT,
    TocDo_n FLOAT,
    Momen_T FLOAT,
    FOREIGN KEY (ID_DuAn) REFERENCES Du_An(ID_DuAn) ON DELETE CASCADE
);

-- Kết quả M2: Đai
CREATE TABLE Thiet_Ke_Dai (
    ID_DuAn INT PRIMARY KEY,
    LoaiDai VARCHAR(10),
    d1 FLOAT, d2 FLOAT,
    KhoangCach_a FLOAT,
    SoDai_Z INT,
    Status_Valid BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (ID_DuAn) REFERENCES Du_An(ID_DuAn) ON DELETE CASCADE
);

-- Kết quả M3: Bánh răng
CREATE TABLE Thiet_Ke_Banh_Rang (
    ID_TkBanhRang INT PRIMARY KEY AUTO_INCREMENT,
    ID_DuAn INT,
    Cap_Truyen VARCHAR(50), -- 'Côn' hoặc 'Trụ'
    z1 INT, z2 INT,
    MoDun FLOAT,
    KhoangCachTruc FLOAT,
    Status_Valid BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (ID_DuAn) REFERENCES Du_An(ID_DuAn) ON DELETE CASCADE
);

-- Kết quả M4: Trục & Ổ lăn (Bổ sung mới)
CREATE TABLE Result_M4_Mechanical (
    ID_DuAn INT PRIMARY KEY,
    d_truc_min FLOAT,
    ID_OLan_Chon INT,
    Status_Valid BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (ID_DuAn) REFERENCES Du_An(ID_DuAn) ON DELETE CASCADE,
    FOREIGN KEY (ID_OLan_Chon) REFERENCES Thu_Vien_O_Lan(ID_OLan)
);

-- ==========================================
-- IV. BẢNG CHECKPOINT – Ghi kết quả từng bước tính toán M1
-- Mỗi bước tính xong → Backend ghi vào đây → Mở MySQL xem ngay
-- ==========================================
CREATE TABLE M1_Checkpoint (
    ID_DuAn INT PRIMARY KEY,

    -- BƯỚC 1: tinh_HieuSuat_Tong()
    eta_dai        FLOAT,        -- Input: η đai
    eta_con        FLOAT,        -- Input: η côn
    eta_tru        FLOAT,        -- Input: η trụ
    eta_o_lan      FLOAT,        -- Input: η ổ lăn
    eta_khop_noi   FLOAT,        -- Input: η khớp nối
    eta_tong       FLOAT,        -- OUTPUT bước 1: η_tổng
    buoc1_ok       BOOLEAN DEFAULT FALSE,
    buoc1_ts       DATETIME,

    -- BƯỚC 2: tinh_P_can_thiet()
    P_tai_W        FLOAT,        -- Input: P_tải (W)
    K_tai          FLOAT,        -- Input: hệ số tải K
    P_can_thiet_kW FLOAT,        -- OUTPUT bước 2: P_ct (kW)
    buoc2_ok       BOOLEAN DEFAULT FALSE,
    buoc2_ts       DATETIME,

    -- BƯỚC 3: tinh_n_so_bo()
    n_lv_vph       FLOAT,        -- Input: n làm việc (v/ph)
    u_dai_sb       FLOAT,        -- Input: u đai sơ bộ
    u_hgt_sb       FLOAT,        -- Input: u HGT sơ bộ
    u_t_so_bo      FLOAT,        -- OUTPUT bước 3: u_t sơ bộ
    n_so_bo_vph    FLOAT,        -- OUTPUT bước 3: n_sb (v/ph)
    buoc3_ok       BOOLEAN DEFAULT FALSE,
    buoc3_ts       DATETIME,

    -- BƯỚC 4: query_dong_co() – Chọn động cơ
    dong_co_chon   VARCHAR(50),  -- OUTPUT bước 4: Model chọn
    P_dong_co_kW   FLOAT,        -- P_dc thực tế
    n_dong_co_vph  FLOAT,        -- n_dc thực tế
    buoc4_ok       BOOLEAN DEFAULT FALSE,
    buoc4_ts       DATETIME,

    -- BƯỚC 5: tinh_toan_he_thong_thuc_te() – Phân phối TST
    u_t_thuc_te    FLOAT,        -- OUTPUT: u_t = n_dc / n_iv
    u_dai_thuc     FLOAT,        -- OUTPUT: u_đai
    u_hop_so       FLOAT,        -- OUTPUT: u_hộp = u_t / u_đai
    u1_con         FLOAT,        -- OUTPUT: u_1 (côn – cấp nhanh)
    u2_tru         FLOAT,        -- OUTPUT: u_2 (trụ – cấp chậm)
    buoc5_ok       BOOLEAN DEFAULT FALSE,
    buoc5_ts       DATETIME,

    -- BƯỚC 6: tinh_thong_so_truc() – Bảng động lực học
    P_dc FLOAT, n_dc FLOAT, T_dc FLOAT,
    P1   FLOAT, n1   FLOAT, T1   FLOAT,
    P2   FLOAT, n2   FLOAT, T2   FLOAT,
    P3   FLOAT, n3   FLOAT, T3   FLOAT,
    buoc6_ok       BOOLEAN DEFAULT FALSE,
    buoc6_ts       DATETIME,

    -- KẾT QUẢ CHÍNH THỨC (thay thế Result_M1_Kinematics)
    ID_DongCo_Chon INT,          -- FK chính thức đến bảng động cơ
    Status_Valid   BOOLEAN DEFAULT TRUE, -- Cờ pipeline: FALSE = cần tính lại M2/M3/M4

    FOREIGN KEY (ID_DuAn) REFERENCES Du_An(ID_DuAn) ON DELETE CASCADE,
    FOREIGN KEY (ID_DongCo_Chon) REFERENCES Thu_Vien_Dong_Co(ID_DongCo)
);

USE dadn;

ALTER TABLE Du_An 
    ADD COLUMN ID_User INT AFTER ID_DuAn,
    ADD CONSTRAINT fk_du_an_user FOREIGN KEY (ID_User) REFERENCES Users(ID_User);

