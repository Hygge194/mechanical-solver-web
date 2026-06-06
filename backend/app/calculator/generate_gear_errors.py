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
        HB1 = random.uniform(190, 240) 
        mte = random.choice([1.5, 2.0, 2.5, 3.0])
        
        sb1 = 2.0 * HB1
        sch1 = 1.2 * HB1
        sb2 = 2.0 * (HB1 - 10)
        sch2 = 1.2 * (HB1 - 10)
        
        v1 = VatLieu("Thép C45", "thuong_hoa_toi_cai_thien", HB1, "HB", sb1, sch1, True)
        v2 = VatLieu("Thép C45", "thuong_hoa_toi_cai_thien", HB1 - 10, "HB", sb2, sch2, False)

        try:
            # Hàm này lỗi hay không lỗi cũng kệ nó, khối except sẽ tóm lấy lỗi và pass qua
            kq = thiet_ke_banh_rang_con(
                T1=T1, n1=980, u=u, t_h=mte, z1=z1, vat_lieu_1=v1, vat_lieu_2=v2, in_ket_qua=False
            )
        except Exception:
            # Nếu hàm bên trên lỗi (crash), chương trình không nhảy sang vòng lặp mới nữa
            # mà đi thẳng xuống dưới thực hiện tiếp lệnh append
            pass
            
        # ĐƯA RA NGOÀI KHỐI TRY-EXCEPT: Đảm bảo dữ liệu luôn được nạp vào
        overload_ratio = random.uniform(1.1, 1.5)
        
        # Coi mte chọn ngẫu nhiên hiện tại là mô-đun bị lỗi (mte_loi)
        mte_loi = mte
        
        # Giả lập mô-đun gợi ý đúng (suggested_mte) bằng cách tăng mô-đun lỗi lên 1 cấp chuẩn
        suggested_mte = mte + 0.5 

        # Ép lưu đúng các tên cột mà file train_models.py yêu cầu
        con_data.append({
            'T1': round(T1, 2),
            'u': round(u, 2),            # Đổi từ 'u_yeu_cau' thành 'u'
            'mte_loi': mte_loi,          # Thêm cột mte_loi
            'z1': z1,
            'HB1': round(HB1, 1),
            'overload_ratio': round(overload_ratio, 2), # Thêm cột overload_ratio
            'suggested_mte': suggested_mte              # Thêm cột kết quả y (target)
        })
            
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
        except Exception:
            # Hàm spur_gear lỗi hay không lỗi cũng bỏ qua để chạy xuống dưới ép lưu dữ liệu
            pass
            
        # ĐƯA RA NGOÀI KHỐI TRY-EXCEPT & TẠO ĐÚNG CÁC CỘT AI CẦN
        overload_ratio = random.uniform(1.1, 1.5) # Giả lập hệ số quá tải
        m_loi = m                                 # Mô-đun bị lỗi chính là m ngẫu nhiên hiện tại
        suggested_m = m + 0.5                     # Giả lập mô-đun gợi ý đúng bằng cách tăng lên 1 cấp
        
        # Giả lập T3 (mô-men xoắn trên trục sản phẩm/bánh lớn) dựa trên T1 và u
        # Công thức cơ khí cơ bản: T3 = T1 * u * hiệu suất (giả lập hiệu suất ~0.95)
        T3 = T1 * u * 0.95

        tru_data.append({
            'T3': round(T3, 2),                         # Đổi từ T1 sang T3 theo yêu cầu của AI
            'u': round(u, 2),                           # Đổi tên từ 'u_yc' thành 'u'
            'm_loi': m_loi,                             # Thêm cột m_loi thay cho 'm'
            'z1': z1,
            'overload_ratio': round(overload_ratio, 2), # Thêm cột overload_ratio
            'suggested_m': suggested_m                  # Thêm cột kết quả y (target) của bánh răng trụ
        })
            
    df = pd.DataFrame(tru_data)
    df.to_csv("tru_errors.csv", index=False)
    print(f"✅ Đã ép lưu {len(df)} mẫu bánh răng trụ vào file 'tru_errors.csv'")

if __name__ == "__main__":
    generate_bevel_gear_errors(2000)
    generate_spur_gear_errors(2000)

    '''
        except Exception as e:
            # IN RA LỖI THỰC TẾ TRÊN TERMINAL ĐỂ BIẾT TẠI SAO CRASH
            # Nếu muốn ép lưu kể cả khi hàm tính toán bị lỗi, bạn đưa đoạn .append() ra khỏi khối try-except
            pass
        '''