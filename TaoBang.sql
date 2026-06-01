CREATE DATABASE IF NOT EXISTS dadn;
USE dadn;

-- du lieu bang tra P1.3
CREATE TABLE Thu_Vien_Dong_Co (
    ID_DongCo INT PRIMARY KEY AUTO_INCREMENT,
    Model VARCHAR(50) NOT NULL,
    CongSuat_kW FLOAT NOT NULL,
    TocDo_vph INT NOT NULL,
    HieuSuat FLOAT NOT NULL,
    CosPhi FLOAT,
    Tmax_Tdn FLOAT,
    Tk_Tdn FLOAT
);

-- bang du an
CREATE TABLE Du_An (
    ID_DuAn INT PRIMARY KEY AUTO_INCREMENT,
    TenDuAn VARCHAR(255),

    -- input user
    P_working_kW FLOAT,
    n_working_vph FLOAT,

    -- ket qua tinh toan
    HieuSuat_Tong FLOAT,
    P_can_thiet_kW FLOAT,
    n_so_bo_vph FLOAT,

    -- ket qua chon
    ID_DongCo_Chon INT,
    U_Tong FLOAT,
    U_Dai FLOAT,
    U_Gear1 FLOAT,
    U_Gear2 FLOAT,

    FOREIGN KEY (ID_DongCo_Chon)
    REFERENCES Thu_Vien_Dong_Co(ID_DongCo)
);

-- bang thong so cac truc
CREATE TABLE Thong_So_Cac_Truc (
    ID_Truc_Result INT PRIMARY KEY AUTO_INCREMENT,
    ID_DuAn INT,
    Ten_Truc VARCHAR(10),
    CongSuat_P FLOAT,
    TocDo_n FLOAT,
    Momen_T FLOAT,

    FOREIGN KEY (ID_DuAn)
    REFERENCES Du_An(ID_DuAn)
    ON DELETE CASCADE
);

-- he so tieu chuan
CREATE TABLE He_So_C_Alpha (
    Goc_Alpha INT PRIMARY KEY,
    Gia_Tri_Ca FLOAT
);

CREATE TABLE Thu_Vien_Dai (
    LoaiDai VARCHAR(10) PRIMARY KEY,
    bt FLOAT,
    b FLOAT,
    h FLOAT,
    DienTich_A FLOAT,
    d1_Min FLOAT,
    d1_Max FLOAT,
    KhoiLuong_qm FLOAT
);

CREATE TABLE Thiet_Ke_Dai (
    ID_TkDai INT PRIMARY KEY AUTO_INCREMENT,
    ID_DuAn INT,
    LoaiDai VARCHAR(10),
    d1 FLOAT,
    d2 FLOAT,
    KhoangCach_a FLOAT,
    ChieuDai_L FLOAT,
    SoDai_Z INT,
    UngSuat_Max FLOAT,

    FOREIGN KEY (ID_DuAn)
    REFERENCES Du_An(ID_DuAn)
    ON DELETE CASCADE,

    FOREIGN KEY (LoaiDai)
    REFERENCES Thu_Vien_Dai(LoaiDai)
);

CREATE TABLE Vat_Lieu_Banh_Rang (
    ID_VatLieu INT PRIMARY KEY AUTO_INCREMENT,
    TenVatLieu VARCHAR(100) NOT NULL,
    DoRan_HB INT,
    Sigma_b FLOAT,
    Sigma_ch FLOAT
);

CREATE TABLE Ket_Qua_Chung (
    ID_KetQua INT PRIMARY KEY AUTO_INCREMENT,
    ID_DuAn INT,
    Model_DongCo VARCHAR(50),

    -- ty so truyen
    ut_thuc FLOAT,
    u_dai FLOAT,
    u_h FLOAT,
    u1_con FLOAT,
    u2_tru FLOAT,

    -- thong so truc
    P_dc FLOAT,
    n_dc FLOAT,
    T_dc FLOAT,

    P1 FLOAT,
    n1 FLOAT,
    T1 FLOAT,

    P2 FLOAT,
    n2 FLOAT,
    T2 FLOAT,

    P3 FLOAT,
    n3 FLOAT,
    T3 FLOAT,

    SaiSo_ut FLOAT,

    FOREIGN KEY (ID_DuAn)
    REFERENCES Du_An(ID_DuAn)
    ON DELETE CASCADE
);

CREATE TABLE Thiet_Ke_Banh_Rang (
    ID_TkBanhRang INT PRIMARY KEY AUTO_INCREMENT,
    ID_DuAn INT,
    Cap_Truyen VARCHAR(50),
    z1 INT,
    z2 INT,
    MoDun FLOAT,
    BeRong_b FLOAT,
    KhoangCachTruc FLOAT,
    Sigma_H FLOAT,
    Sigma_F FLOAT,

    FOREIGN KEY (ID_DuAn)
    REFERENCES Du_An(ID_DuAn)
    ON DELETE CASCADE
);

-- luu session project
CREATE TABLE Project_Sessions (
    session_id VARCHAR(100) PRIMARY KEY,
    user_name VARCHAR(100),
    p_input FLOAT,
    n_input FLOAT,
    l_input FLOAT,
    selected_motor_id INT,
    status VARCHAR(20) DEFAULT 'M1_IN_PROGRESS',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Bảng tài khoản người dùng
CREATE TABLE IF NOT EXISTS Users (
    ID_User INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    FullName VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);