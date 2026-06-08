from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.motor_service import get_motor_recommendations
from services.auth_service import register_user, authenticate_user
import joblib
import pandas as pd
import os

app = FastAPI(title="Phần mềm thiết kế hệ dẫn động - BK")

# Cấu hình CORS để cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# KHỞI TẠO VÀ TẢI MÔ HÌNH AI DOCTOR (BƯỚC CHÈN MỚI)
# -----------------------------------------------------------------------------
# Xác định đường dẫn tuyệt đối hoặc tương đối tới file .pkl của bạn
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_CON_PATH = os.path.join(BASE_DIR, "calculator", "ai_doctor_con.pkl")
MODEL_TRU_PATH = os.path.join(BASE_DIR, "calculator", "ai_doctor_tru.pkl")

model_con = None
model_tru = None

try:
    if os.path.exists(MODEL_CON_PATH):
        model_con = joblib.load(MODEL_CON_PATH)
        print("🤖 AI Doctor: Đã tải thành công mô hình Bánh Răng Côn!")
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy file mô hình côn tại {MODEL_CON_PATH}")

    if os.path.exists(MODEL_TRU_PATH):
        model_tru = joblib.load(MODEL_TRU_PATH)
        print("🤖 AI Doctor: Đã tải thành công mô hình Bánh Răng Trụ!")
    else:
        print(f"⚠️ Cảnh báo: Không tìm thấy file mô hình trụ tại {MODEL_TRU_PATH}")
except Exception as e:
    print(f"❌ Lỗi nghiêm trọng khi tải mô hình AI: {e}")

@app.get("/")
def read_root():
    return {"message": "Backend API đang hoạt động bình thường! Hãy chạy ứng dụng từ giao diện Frontend (HTML).", "version": "1.0.0"}

# --- AUTHENTICATION ROUTES ---

@app.post("/api/v1/auth/register")
async def register(data: dict):
    try:
        result = register_user(data)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/login")
async def login(data: dict):
    try:
        result = authenticate_user(data)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# --- MOTOR CALCULATION ROUTES ---


@app.post("/api/v1/calculate/motor")
async def calculate_motor(data: dict):
    """
    Endpoint nhận yêu cầu tính toán động cơ từ ReactJS
    Dữ liệu truyền vào dạng JSON: { "p_tai": 5500, "n_tai": 70, "hieu_suat": {...} }
    """
    try:
        result = get_motor_recommendations(data)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/v1/calculate/motor/step3_4")
async def calculate_motor_step3_4(data: dict):
    """
    Endpoint nhận yêu cầu kiểm nghiệm động cơ và tính bảng động lực học
    Dữ liệu JSON: { "motor": {"code": "DK..", "P": 5.5, "n": 1450, "tk_tdn": 2.2}, "k_qt": 1.3, "n_iv": 70 }
    """
    try:
        motor_data = data.get("motor", {})
        k_qt = data.get("k_qt", 1.3)
        n_iv = data.get("n_iv", 70)
        
        from calculator.motor import kiem_nghiem_khoi_dong, tinh_toan_he_thong_thuc_te, tinh_thong_so_truc
        
        # 1. Validation (Kiểm nghiệm khởi động)
        dc_row = {"Tk_Tdn": motor_data.get("tk_tdn", 0)}
        is_valid, msg = kiem_nghiem_khoi_dong(dc_row, k_qt)
        
        # 2. Bảng động lực học
        fake_dc_chon = {"TocDo_vph": motor_data.get("n", 1450), "Model": motor_data.get("code", "")}
        # Tỉ số truyền tổng và phân phối
        ratios_dict = tinh_toan_he_thong_thuc_te(fake_dc_chon, n_iv)
        
        u_list = [ratios_dict["u_dai"], ratios_dict["u_1"], ratios_dict["u_2"]]
        eta_list = {
            "dai": 0.96, "con": 0.97, "tru": 0.98, "o_lan": 0.995, "khop_noi": 0.99
        }
        
        kinematics = tinh_thong_so_truc(motor_data.get("P", 0), motor_data.get("n", 1450), u_list, eta_list)
        
        return {
            "status": "success",
            "validation": { "is_valid": is_valid, "message": msg },
            "kinematics": kinematics,
            "ratios": ratios_dict
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


# --- BELT CALCULATION ROUTE ---

@app.post("/api/v1/calculate/belt")
async def calculate_belt(data: dict):
    """
    Endpoint tính toán bộ truyền đai hình thang.
    Payload JSON từ frontend (dai.js → buildPayload()):
      {
        "power":       <float>  – công suất P1 (kW),
        "speed":       <float>  – tốc độ n1 (v/ph),
        "ratio":       <float>  – tỉ số truyền đai ud,
        "load_factor": <float>  – hệ số tải Kd (mặc định 1.2),
        "slip":        <float>  – hệ số trượt eps (mặc định 0.02),
        "belt_type":   <str>    – loại đai ("auto" hoặc "A","Б",...),
        "lifetime":    <float>  – tuổi thọ (không dùng trong tính toán, bỏ qua)
      }
    """
    try:
        from calculator.dai import tinh_bo_truyen_dai

        P1  = float(data.get("power",       0))
        n1  = float(data.get("speed",       0))
        ud  = float(data.get("ratio",       0))
        Kd  = float(data.get("load_factor", 1.2))
        eps = float(data.get("slip",        0.02))

        if P1 <= 0 or n1 <= 0 or ud <= 0:
            raise ValueError(f"Thông số không hợp lệ: P1={P1}, n1={n1}, ud={ud}")

        kq = tinh_bo_truyen_dai(P1=P1, n1=n1, ud=ud, Kd=Kd, eps=eps, verbose=False)

        # Map kết quả sang schema frontend kỳ vọng (xem runLocal() trong dai.js)
        result = {
            "belt_type": kq.get("loai_dai"),
            "d1":        kq.get("d1"),
            "d2":        kq.get("d2"),
            "v":         kq.get("v"),
            "L":         kq.get("L"),
            "a":         kq.get("a"),
            "a_dc":      kq.get("a_dieu_chinh_min"),   # khoảng điều chỉnh min
            "a_dc_max":  kq.get("a_dieu_chinh_max"),
            "alpha1":    kq.get("alpha1"),
            "u_actual":  kq.get("u_thucte"),
            "delta_u":   kq.get("sai_so_pct"),
            "Ca":        kq.get("Ca"),
            "Cl":        kq.get("Cl"),
            "Cu":        kq.get("Cu"),
            "Cz":        kq.get("Cz"),
            "Z":         kq.get("Z"),
            "B":         kq.get("B"),
            "da1":       kq.get("da1"),
            "da2":       kq.get("da2"),
            "F0":        kq.get("F0"),
            "Ft":        kq.get("Ft"),
            "Fr":        kq.get("Fr"),
            "Fv":        kq.get("Fv"),
            "P0":        kq.get("P0"),
            "log":       kq.get("log", []),
            "_source":   "backend",
        }

        return {"status": "success", "data": result}

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/v1/predict/bevel-gear")
async def predict_bevel_gear(data: dict):
    """
    API tiếp nhận thông số bánh răng côn bị lỗi từ Frontend 
    và dùng mô hình AI (Random Forest) để dự đoán mô-đun 'suggested_mte' tối ưu.
    """
    if model_con is None:
        raise HTTPException(status_code=503, detail="Mô hình AI Bánh răng côn hiện chưa được tải thành công trên hệ thống.")
    
    try:
        # 1. Trích xuất dữ liệu từ payload nhận về từ Frontend
        T1 = float(data.get("T1", 0))
        u = float(data.get("u", 0))
        mte_loi = float(data.get("mte_loi", 0))
        z1 = int(data.get("z1", 0))
        HB1 = float(data.get("HB1", 0))
        overload_ratio = float(data.get("overload_ratio", 1.3)) # Mặc định 1.3 nếu frontend không truyền

        # 2. Tạo DataFrame đúng cấu trúc các trường thông tin mà AI đã học từ Bước 2
        input_df = pd.DataFrame([{
            'T1': T1,
            'u': u,
            'mte_loi': mte_loi,
            'z1': z1,
            'HB1': HB1,
            'overload_ratio': overload_ratio
        }])

        # 3. Chạy dự đoán bằng mô hình Random Forest
        raw_prediction = model_con.predict(input_df)[0]

        # 4. Quy đổi số thực dự đoán về mô-đun tiêu chuẩn gần nhất trong thiết kế cơ khí
        standard_modules = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0]
        suggested_mte = min([m for m in standard_modules if m >= raw_prediction], default=max(standard_modules))

        return {
            "status": "success",
            "data": {
                "raw_predicted_mte": round(raw_prediction, 4),
                "suggested_mte": suggested_mte
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/v1/predict/spur-gear")
async def predict_spur_gear(data: dict):
    """
    API tiếp nhận thông số bánh răng trụ bị lỗi từ Frontend
    và dùng mô hình AI để dự đoán mô-đun 'suggested_m' phù hợp nhất.
    """
    if model_tru is None:
        raise HTTPException(status_code=503, detail="Mô hình AI Bánh răng trụ hiện chưa được tải thành công trên hệ thống.")
    
    try:
        T3 = float(data.get("T3", 0))
        u = float(data.get("u", 0))
        m_loi = float(data.get("m_loi", 0))
        z1 = int(data.get("z1", 0))
        overload_ratio = float(data.get("overload_ratio", 1.3))

        input_df = pd.DataFrame([{
            'T3': T3,
            'u': u,
            'm_loi': m_loi,
            'z1': z1,
            'overload_ratio': overload_ratio
        }])

        raw_prediction = model_tru.predict(input_df)[0]

        standard_modules = [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0]
        suggested_m = min([m for m in standard_modules if m >= raw_prediction], default=max(standard_modules))

        return {
            "status": "success",
            "data": {
                "raw_predicted_m": round(raw_prediction, 4),
                "suggested_m": suggested_m
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- REPORT GENERATION ROUTE ---

from utils.report import generate_report

@app.post("/api/v1/report/generate")
async def api_generate_report(payload: dict):
    """
    Endpoint nhận JSON project data từ frontend và trả về file Word stream.
    """
    try:
        file_stream = generate_report(payload)
        return StreamingResponse(
            file_stream, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=Thuyet_Minh_Do_An.docx"}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Lỗi tạo báo cáo: {str(e)}")

# Lệnh chạy server: python -m uvicorn main:app --reload