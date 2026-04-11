from fastapi import FastAPI, HTTPException
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
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/auth/login")
async def login(data: dict):
    try:
        result = authenticate_user(data)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

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
        fake_dc_chon = {"VanToc_vph": motor_data.get("n", 1450), "Model": motor_data.get("code", "")}
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

# Lệnh chạy server: python -m uvicorn main:app --reload