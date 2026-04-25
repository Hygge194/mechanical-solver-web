from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.motor_service import get_motor_recommendations, finalize_m1_with_checkpoint
from services.auth_service import register_user, authenticate_user
from services.project_service import create_new_project


app = FastAPI(title="Phần mềm thiết kế hệ dẫn động - BK")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend API đang hoạt động bình thường!", "version": "1.0.0"}

# ── AUTH ──────────────────────────────────────────────────────

@app.post("/api/v1/auth/register")
async def register(data: dict):
    try:
        result = register_user(data)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/v1/auth/login")
async def login(data: dict):
    try:
        result = authenticate_user(data)
        return {"status": "success", "data": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")

# ── PROJECT ROUTES ─────────────────────────────────────────────

@app.post("/api/v1/projects/create")
async def create_project(data: dict):
    """
    Tạo dự án mới: { "user_id": 1, "project_name": "Dự án A" }
    """
    try:
        u_id = data.get("user_id")
        name = data.get("project_name", "Dự án mới")
        p_id = create_new_project(u_id, name)
        return {"status": "success", "project_id": p_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ── MOTOR CALCULATION ─────────────────────────────────────────

@app.post("/api/v1/calculate/motor")
async def calculate_motor(data: dict):
    """
    Bước 1–4: Tính η_tổng, P_ct, n_sb và gợi ý 3 động cơ.

    Body JSON:
        { "p_tai_w": 5500, "n_lv": 70, "project_id": 1 }

    Nếu có 'project_id' → ghi checkpoint bước 1-4 vào M1_Checkpoint ngay lập tức.
    Không có 'project_id' → chỉ trả kết quả, không ghi DB.
    """
    try:
        project_id = data.get("project_id", None)       # ← đây là chìa khoá
        result = get_motor_recommendations(data, project_id=project_id)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.post("/api/v1/calculate/motor/step3_4")
async def calculate_motor_step3_4(data: dict):
    """
    Bước 5–6: Kiểm nghiệm khởi động + bảng động lực học.

    Body JSON:
        {
          "motor": {"code": "4A100L4Y3", "P": 5.5, "n": 1445, "tk_tdn": 2.0},
          "k_qt": 1.3, "n_iv": 70,
          "project_id": 1
        }

    Nếu có 'project_id' → ghi checkpoint bước 5 và 6 vào M1_Checkpoint.
    """
    try:
        motor_data = data.get("motor", {})
        k_qt       = data.get("k_qt", 1.3)
        n_iv       = data.get("n_iv", 70)
        project_id = data.get("project_id", None)

        from calculator.motor import kiem_nghiem_khoi_dong, tinh_toan_he_thong_thuc_te, tinh_thong_so_truc

        # Bước 5a: Kiểm nghiệm khởi động
        dc_row = {"Tk_Tdn": motor_data.get("tk_tdn", 0)}
        is_valid, msg = kiem_nghiem_khoi_dong(dc_row, k_qt)

        # Bước 5b: Phân phối tỉ số truyền
        fake_dc = {"VanToc_vph": motor_data.get("n", 1450), "Model": motor_data.get("code", "")}
        ratios_dict = tinh_toan_he_thong_thuc_te(fake_dc, n_iv)

        # Bước 6: Bảng động lực học
        u_list   = [ratios_dict["u_dai"], ratios_dict["u_1"], ratios_dict["u_2"]]
        eta_list = {"dai": 0.96, "con": 0.97, "tru": 0.98, "o_lan": 0.995, "khop_noi": 0.99}
        kinematics = tinh_thong_so_truc(motor_data.get("P", 0), motor_data.get("n", 1450), u_list, eta_list)

        # Ghi checkpoint bước 5 & 6 nếu có project_id
        if project_id:
            finalize_m1_with_checkpoint(
                selected_motor=motor_data,
                ratios=ratios_dict,
                efficiency_data=eta_list,
                project_id=project_id
            )

        return {
            "status": "success",
            "validation": {"is_valid": is_valid, "message": msg},
            "kinematics": kinematics,
            "ratios": ratios_dict
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Lệnh chạy server: python -m uvicorn main:app --reload