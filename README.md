# ⚙️ MechaMix - Mechanical Solver Web

**Hệ sinh thái giải pháp thiết kế truyền động cơ khí tự động hóa & tích hợp AI**

Đây là một nền tảng web toàn diện được thiết kế chuyên biệt để tự động hóa, tăng tốc độ tính toán, hạn chế sai sót số học và trực quan hóa toàn bộ tiến trình thực hiện Đồ án chi tiết máy / Thiết kế hệ thống dẫn động cơ khí.

---

## 🚀 Các Tính Năng Cốt Lõi (Core Features)

Ứng dụng được chia thành nhiều luồng trải nghiệm người dùng, từ lúc bắt đầu truy cập đến khi xuất báo cáo hoàn chỉnh:

### 1. Hệ thống Xác Thực & Quản Lý Người Dùng
- **Bảo mật chuẩn Quốc tế**: Tuyến phòng thủ bảo mật mã hóa mật khẩu bằng thư viện **Bcrypt** (tự động cắt gọt và mã hóa chuẩn UTF-8), tránh lưu Plain-text trong cơ sở dữ liệu.
- **Cơ chế Phiên làm việc (Session)**: Quản lý đăng nhập bằng công nghệ **JWT (JSON Web Tokens)** bền vững, lưu trữ qua `localStorage` và bảo vệ các trang khỏi truy cập trái phép.
- **Giao diện Sang trọng**: Form đăng nhập & Dashboard thiết kế theo xu hướng Glassmorphism hiện đại.

### 2. Module Tính Toán Kỹ Thuật Chuyên Sâu
- **M1 (Động cơ & Động lực học)**: Tự động tra cứu CSDL để đề xuất top 3 động cơ tối ưu nhất. Phân bổ tỉ số truyền và lan truyền các thông số ($P$, $n$, $T$) trên từng trục. Biểu đồ động học trực quan.
- **M2 (Bộ Truyền Đai)**: Tính toán thiết kế bộ truyền đai hình thang (xác định loại đai, số đai, khoảng cách trục, lực căng đai...).
- **M3 (Bánh Răng Côn)**: Tính toán thông số động học, kiểm nghiệm độ bền tiếp xúc, mỏi uốn, và hệ số tải trọng động. **Đặc biệt:** Tích hợp Machine Learning (Random Forest) để dự đoán và gợi ý mô-đun $m_{te}$ tối ưu khi có thông số đầu vào bị lỗi.
- **M4 (Bánh Răng Trụ)**: Tính toán thiết kế chi tiết bộ truyền bánh răng trụ răng thẳng/nghiêng. **Đặc biệt:** Tích hợp Machine Learning để tự động dự đoán mô-đun $m$ dựa trên tải trọng và tỉ số truyền.

### 3. Tự Động Xuất Báo Cáo Thuyết Minh (Word)
- **Tự động hóa 100%**: Thu thập toàn bộ dữ liệu từ M1 đến M4 đang lưu trữ trên trình duyệt của người dùng.
- **Định dạng Chuẩn Form**: Chèn tự động dữ liệu vào file Word (`.docx`) chuyên nghiệp, sẵn sàng để in ấn hoặc chỉnh sửa thêm.

---

## 💻 Công Nghệ Lõi (Tech Stack)

Dự án tuân theo kiến trúc **"Thin-Client, Thick-Backend"**. Trình duyệt giao diện chỉ đảm đương đồ họa, mọi logic sức mạnh tính toán và Machine Learning được xử lý tại Máy Chủ.

### Máy Chủ Tính Toán (Backend)
- **Ngôn ngữ Core**: Python 3.10+
- **Kiến trúc API**: FastAPI (hỗ trợ RESTful API tốc độ cực cao)
- **Cơ sở dữ liệu**: MySQL Server kết hợp `pymysql`.
- **AI & Data Science**: `scikit-learn`, `pandas`, `joblib`.
- **Báo cáo & Bảo mật**: `python-docx`, `passlib`, `bcrypt`, `PyJWT`.

### Giao Diện (Frontend)
- **Hệ Thiết Kế**: **Vanilla HTML/CSS/JS** không sử dụng framework cồng kềnh, tối giản nhưng đạt hiệu ứng thị giác mức Premium (Neon glows, Transitions, Mesh background).
- **Typography**: Kết hợp Google Fonts *Plus Jakarta Sans* và *JetBrains Mono*.

---

## ⚙️ Hướng Dẫn Cài Đặt Tại Máy Cục Bộ (Local Deployment)

### Yêu cầu tiên quyết:
- Python 3.10+
- MySQL Server Port 3306
- Trình duyệt Web hiện đại (Chrome/Edge/Firefox)
- Extension Live Server trên VS Code (để chạy frontend)

### Các Bước Cài Đặt (Quick Start)

**1. Khởi tạo Database (MySQL):**
* Chạy 2 file `TaoBang.sql` và `UpdateAuth.sql` vào MySQL để tạo Cấu trúc CSDL `dadn` cùng với bảng `Users`.
* Chạy tiếp `DataSeeding.sql` để thiết lập thư viện động cơ mẫu có thực dựa theo sách Thiết kế.
* Cập nhật mật khẩu MySQL của bạn trong file `backend/app/database/config.py`.

**2. Bật Backend Server:**
Mở Terminal tại thư mục gốc của dự án và chạy các lệnh sau:
```bash
# Di chuyển tới máy chủ API
cd backend/app

# Cài đặt các thư viện lõi, bảo mật, và xử lý Word
pip install fastapi uvicorn pymysql passlib bcrypt==3.2.2 PyJWT python-dotenv python-docx

# Cài đặt các thư viện cho mô hình AI
pip install pandas scikit-learn joblib openpyxl

# Boot máy chủ chạy ngầm ở port 8000
python -m uvicorn main:app --reload
```

**3. Khởi Động Giao Diện:**
* Mở thư mục `frontend` trên IDE (VD: VS Code).
* Chạy **Live Server** bắt đầu từ file `register.html`.
* *Tạo một tài khoản, đăng nhập, tính toán các Module và dùng tính năng Xuất báo cáo Word để trải nghiệm.*
