from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from services.motor_service import get_motor_recommendations
from services.auth_service import register_user, authenticate_user

app = FastAPI(title="Phần mềm thiết kế hệ dẫn động - BK")

# Cấu hình CORS để cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# Lệnh chạy server: python -m uvicorn main:app --reload

# --- REPORT GENERATION ROUTE ---

@app.post("/api/v1/report/generate")
async def generate_report_endpoint(data: dict):
    """
    Endpoint nhận toàn bộ JSON PROJECT_DATA từ trình duyệt
    để sinh file báo cáo Word (DOCX) rồi trả thẳng về cho người dùng tải xuống.
    """
    try:
        from utils.report import generate_report
        file_stream = generate_report(data)
        
        headers = {
            'Content-Disposition': 'attachment; filename="Thuyet_Minh_Do_An.docx"'
        }
        
        return StreamingResponse(
            file_stream, 
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
            headers=headers
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))