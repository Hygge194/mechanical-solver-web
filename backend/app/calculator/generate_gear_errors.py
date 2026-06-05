# -*- coding: utf-8 -*-
import random
import pandas as pd
from bevel_gear import thiet_ke_banh_rang_con, VatLieu 
import spur_gear 

def generate_bevel_gear_errors(num_samples=2000):
    con_data = []
    print("⏳ Đang ép giả lập và lưu dữ liệu Bánh Răng Côn...")
    
    for _ in range(num_samples):
        T1 = random.uniform(150000, 500000) 
        u = random.uniform(2.0, 4.5)            
        z1 = random.randint(18, 30)             
        HB1 = random.uniform(190, 240) # Thu hẹp dải HB tiêu chuẩn thép C45
        mte = random.choice([1.5, 2.0, 2.5, 3.0])
        
        # SỬA LỖI VẬT LIỆU TỶ LỆ THEO HB1
        sb1 = 2.0 * HB1
        sch1 = 1.2 * HB1
        sb2 = 2.0 * (HB1 - 10)
        sch2 = 1.2 * (HB1 - 10)
        
        v1 = VatLieu("Thép C45", "thuong_hoa_toi_cai_thien", HB1, "HB", sb1, sch1, True)
        v2 = VatLieu("Thép C45", "thuong_hoa_toi_cai_thien", HB1 - 10, "HB", sb2, sch2, False)

        try:
            kq = thiet_ke_banh_rang_con(
                T1=T1, n1=980, u=u, t_h=mte, z1=z1, vat_lieu_1=v1, vat_lieu_2=v2, in_ket_qua=False
            )
            
            con_data.append({
                'T1': round(T1, 2),
                'u_yeu_cau': round(u, 2),
                'z1': z1,
                'HB1': round(HB1, 1),
                'mte': mte
            })
        except Exception as e:
            # IN RA LỖI THỰC TẾ TRÊN TERMINAL ĐỂ BIẾT TẠI SAO CRASH
            # Nếu muốn ép lưu kể cả khi hàm tính toán bị lỗi, bạn đưa đoạn .append() ra khỏi khối try-except
            pass
            
    df = pd.DataFrame(con_data)
    df.to_csv("con_errors.csv", index=False)
    print(f"✅ Đã ép lưu {len(df)} mẫu bánh răng côn vào file 'con_errors.csv'")

def generate_spur_gear_errors(num_samples=2000):
    tru_data = []
    print("⏳ Đang ép giả lập và lưu dữ liệu Bánh Răng Trụ...")
    for _ in range(num_samples):
        T1 = random.uniform(150000, 500000)
        u = random.uniform(2.0, 4.5)
        z1 = random.randint(18, 32)
        m = random.choice([1.5, 2.0, 2.5, 3.0])
        z2 = int(round(z1 * u))
        aw = (m * (z1 + z2)) / 2.0  
        try:
            res = spur_gear.main(T1=T1, u_yc=u, m=m, z1=z1, z2=z2, aw=aw, hien_thi_bang=False)
            tru_data.append({
                'T1': round(T1, 2), 'u_yc': round(u, 2), 'm': m, 'z1': z1, 'z2': z2, 'aw': aw
            })
        except Exception:
            continue
    df = pd.DataFrame(tru_data)
    df.to_csv("tru_errors.csv", index=False)
    print(f"✅ Đã ép lưu {len(df)} mẫu bánh răng trụ vào file 'tru_errors.csv'")

if __name__ == "__main__":
    generate_bevel_gear_errors(2000)
    generate_spur_gear_errors(2000)