#  MechaMix - Mechanical Solver Web

**Hệ sinh thái giải pháp thiết kế truyền động cơ khí tự động hóa**

Đây là một nền tảng web toàn diện được thiết kế chuyên biệt để tự động hóa, tăng tốc độ tính toán, hạn chế sai sót số học và trực quan hóa toàn bộ tiến trình thực hiện Đồ án chi tiết máy / Thiết kế hệ thống dẫn động cơ khí.

---

## Kiến trúc & Các Luồng Tính Năng (Features)

Ứng dụng được chia thành nhiều luồng trải nghiệm người dùng, từ lúc bắt đầu truy cập đến khi hoàn tất một đồ án:

### 1. Hệ thống Xác Thực Người Dùng (Authentication)
Dữ liệu cá nhân hóa là yếu tố cốt lõi của MechaMix. Hệ thống trang bị cơ chế bảo mật nghiêm ngặt và hiện đại:
- **Đăng ký / Đăng nhập (Register/Login)**: Sử dụng Form đăng nhập thiết kế theo xu hướng Glassmorphism sang trọng.
- **Bảo mật chuẩn Quốc tế**: Tuyến phòng thủ bảo mật mã hóa mật khẩu bằng thư viện **Bcrypt** (tự động cắt gọt và mã hóa chuẩn UTF-8), tránh lưu Plain-text trong cơ sở dữ liệu.
- **Cơ chế Phiên làm việc (Session)**: Quản lý đăng nhập bằng công nghệ **JWT (JSON Web Tokens)** bền vững, lưu trữ qua `localStorage` và tự động điều hướng bảo vệ các trang chặn truy cập trái phép.

### 2. Bảng Điều Khiển Trung Tâm (MechaMix Dashboard)
Đóng vai trò là "Trạm chỉ huy" của người kỹ sư cơ khí:
- **Trực quan Cấu trúc**: Cung cấp Menu Sidebar điều hướng toàn diện đến các Module (Nhập liệu, Bánh răng Côn-Trụ, Trục & Ổ lăn, Giao diện AI/ML).
- **Cá nhân hóa Dữ liệu**: Quản lý hồ sơ người dùng (Hiển thị Avatar, Tên người dùng động) nhờ bóc tách JWT Token.
- **Truy cập nhanh (Quick Actions)**: Chứa các phím tắt "Tạo Dự Án Mới", "Tiếp tục Dự án gần đây", và Hướng dẫn sử dụng.

### 3. Module M1: Tính toán chọn Động cơ & Động lực học
Thành phần hạt nhân của hệ thống giải quyết "Bước 1" của đồ án:
- **Tra cứu CSDL Động Cơ**: Tự động lấy danh sách Động cơ tiêu chuẩn khớp với thông số ($P_{ct}$ và Vi sai số vòng quay).
- **Bộ Lọc Thông Minh (Top-3 Ranking)**: Không còn mất thời gian lật sách, AI tự động gợi ý top 3 động cơ có hiệu năng và tỉ số truyền khớp nhất.
- **Động Lực Học Tự Động**: Hệ thống lập tức phân bổ Tỉ số truyền tổng ($u_t$) cho các cụm (Đai, Côn, Trụ...) và lan truyền nghịch lực $P$, $n$, $T$ trên từng trục.
- **Biểu đồ động (Interactive Charts)**: Render ra giao diện HTML đồ thị biểu diễn biến thiên của Momen xoắn theo tốc độ của các trục dẫn để đối chiếu ngay lập tức.

### 4. Các Module Chuyên sâu Kỹ thuật (M2 - M4)
Hệ thống đã hoàn thiện các module tính toán thiết kế bộ truyền động:
- **M2 (Bộ Truyền Đai)**: Tính toán thiết kế bộ truyền đai hình thang (xác định loại đai, số đai, khoảng cách trục, lực căng đai...).
- **M3 (Bánh Răng Côn)**: Module tính toán thông số động học, kiểm nghiệm độ bền tiếp xúc, mỏi uốn, tính toán hệ số tải trọng động cho bánh răng côn.
- **M4 (Bánh Răng Trụ)**: Module tính toán thiết kế chi tiết bộ truyền bánh răng trụ răng thẳng/nghiêng.
*(Các phần Tính toán Trục, Ổ lăn, AI Optimization, và Xuất PDF đang nằm trong lộ trình phát triển tiếp theo)*

---

## Công Nghệ Lõi (Tech Stack)

Dự án tuân theo kiến trúc **"Thin-Client, Thick-Backend"**. Trình duyệt giao diện chỉ đảm đương đồ họa, mọi logic sức mạnh tính toán số thực dấu phẩy động (float math) siêu chính xác được nhường lại cho Máy Chủ.

### Máy Chủ Tính Toán (Backend)
- **Ngôn ngữ Core**: Python 3.10+
- **Kiến trúc API**: FastAPI (hỗ trợ RESTful API bất đồng bộ tốc độ cực cao)
- **Bảo Mật**: `Passlib`, `Bcrypt`, `PyJWT`.
- **Cơ sở dữ liệu**: MySQL Server kết hợp Python `pymysql` driver.

### Giao Diện (Frontend)
- **Hệ Thiết Kế**: **Vanilla HTML/CSS/JS** không sử dụng framework cồng kềnh, tối giản mà đạt hiệu ứng thị giác mức Premium (Neon glows, Transitions, Mesh background).
- **Kiến trúc CSS**: Bám sát UI/UX hiện đại (Dashboards, Flip-Cards, Interactive Charts).
- **Typography**: Kết hợp Google Fonts *Plus Jakarta Sans* và *JetBrains Mono*.

---

## Hướng Dẫn Cài Đặt Tại Máy Cục Bộ (Local Deployment)

### Yêu cầu tiên quyết:
- Python 3.10+
- MySQL Server Port 3306.
- Extension Live Server trên VS Code.

### Cài Đặt Nhanh (Quick Start)

**1. Khởi tạo Database:**
*   Chạy 2 file `TaoBang.sql` và `UpdateAuth.sql` vào MySQL để tạo Cấu trúc CSDL `dadn` cùng với bảng `Users`.
*   Chạy tiếp `DataSeeding.sql` để thiết lập thư viện động cơ mẫu có thực dựa theo sách Thiết kế.

**2. Bật Backend Server:**
Mở Terminal tại nhánh gốc của dự án:
```bash
# Di chuyển tới máy chủ API
cd backend/app

# Cài đặt nền tảng
pip install fastapi uvicorn pymysql passlib bcrypt==3.2.2 PyJWT python-dotenv

# Boot máy chủ chạy ngầm ở port 8000
python -m uvicorn main:app --reload

#Cài đặt để chạy AI
python -m pip install pandas openpyxl

```

**3. Khởi Động Giao Diện:**
*   Mở thư mục `frontend` trên IDE.
*   Chạy Live Server từ file `login.html`.
*   *Tạo một tài khoản, đăng nhập và tận hưởng ứng dụng qua Dashboard.*

Note: 
dai.py, config.py, env: password


