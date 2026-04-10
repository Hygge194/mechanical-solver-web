# ⚙️ MechaMix - Mechanical Solver Web

**Hệ sinh thái giải pháp thiết kế truyền động cơ khí tự động hóa**

Đây là một nền tảng tính toán hệ thống dẫn động cơ khí được lên ý tưởng và phát triển dành cho mục đích đẩy tốc độ tính toán đồ án thiết kế hệ thống dẫn động cơ khí lên gấp nhiều lần, hạn chế các sai sót số học, trực quan hóa tiến trình và tự động tra cứu thư viện.

---

## 🚀 Tính năng nổi bật (Theo Modules Tiến trình)

### 1. 🎯 Module M1: Tính toán chọn Động cơ & Động lực học
- **Tra cứu Cơ sở dữ liệu**: Lọc thư viện Động cơ tự động dựa trên số vòng quay và công suất cần thiết.
- **Bộ lọc thông minh**: Xếp hạng động cơ tối ưu dựa trên chỉ số sai lệch tốc độ thấp nhất và công suất sát nhất.
- **Kiểm nghiệm khởi động**: Kiểm toán dựa trên hệ số ($T_k/T_{dn} \geq K_{qt}$).
- **Bảng Động lực học Tự động**: Tự động hóa phân phối Tỷ số truyền và truyền ngược $P$, $n$, $T$ cho các trục dẫn.
- **Biểu đồ động (Animation)**: Hiển thị trực quan nghịch biến giữa Momen xoắn và tốc độ quay trên các trục truyền.

### 2. 🔄 Module M2-M4: Thiết kế Bộ truyền & Bánh răng (Đang phát triển)
- **Bộ truyền đai (M2)**: Xác định đường kính, khoảng cách trục, sức căng và số đai.
- **Bánh răng Côn - Trụ (M3)**: Xây dựng hệ số mỏi, kiểm nghiệm bền tiếp xúc và bền uốn.
- **Hệ thống Trục & Ổ lăn (M4)**: Đánh giá tuổi thọ kết cấu trục.

---

## 🛠️ Công nghệ & Kiến trúc Hệ thống

### Kiến trúc: "Thin-Client, Thick-Backend"
Toàn bộ các logic tính toán nặng của đồ án cơ khí được chuyển giao cho sức mạnh của Python xử lý tại máy chủ. Giao diện chỉ làm nhiệm vụ tương tác và hiển thị (Tránh làm tròn sai lệch trên Client JS).

### 🖥️ Backend (Máy chủ Tính toán)
- **Ngôn ngữ**: Python 3.10+
- **Framework API**: FastAPI (Mạnh mẽ, hỗ trợ bất đồng bộ, tốc độ truy xuất cực cao)
- **Quản trị Cơ sở dữ liệu**: MySQL Server
- **Truy vấn**: Pymysql (Native Queries)

### 🎨 Frontend (Giao diện Người dùng)
- **Cấu trúc**: HTML5 / CSS3 (Thiết kế hệ thống Design System độc quyền `MechaMix Concept`)
- **Tương tác**: Vanilla JavaScript (ES6+ gốc, không phụ thuộc Framework rườm rà)
- **Kiến trúc Layout**: Flexbox / CSS Grid, CSS Animations.

---

## 📋 Hướng dẫn Khởi chạy trên Local

### Yêu cầu môi trường
- Python (v3.10 trở lên)
- MySQL Server (Đã cài đặt và đang chạy)
- VS Code với extension Live Server (Khuyến nghị)

### Bước 1: Khởi tạo Database (MySQL)
1. Mở app MySQL (hoặc phpMyAdmin) và tạo database (vd: `dadn`).
2. Mở file `TaoBang.sql` ở thư mục gốc và Run để thiết lập các cột Bảng CSDL.
3. Mở file `DataSeeding.sql` để Seed sẵn các bộ thư viện Động cơ có thật ở trong sách giáo khoa vào hệ thống.
4. Mở file thư mục `backend/app/database/mysql_db.py` và sửa tham số kết nối (User, Pass, DB_Name) cho khớp với máy cục bộ của bạn.

### Bước 2: Khởi động Máy chủ Tính toán (Backend)
1. Mở terminal tại thư mục gốc của project, di chuyển sâu vào thư mục con:
   ```bash
   cd backend/app
   ```
2. Cài đặt các thư viện cần thiết (nếu chưa cài):
   ```bash
   pip install fastapi uvicorn pymysql
   ```
3. Bật máy chủ với chế độ lắng nghe liên tục:
   ```bash
   python -m uvicorn main:app --reload
   ```
   > Hiển thị thông báo **"Application startup complete"** tại `http://127.0.0.1:8000` là thành công! (Lưu ý: Không tắt Terminal này).

### Bước 3: Mở trực tiếp Giao diện (Frontend)
Vì dự án dùng HTML tĩnh thuần túy không cần compiler phức tạp:
1. Bạn có thể kéo thả trực tiếp file như `frontend/m1/m1_input_validation.html` vào Chrome / Edge để dùng.
2. **Khuyến nghị tốt nhất**: Mở thư mục code trong VS Code, chuột phải vào file `.html` => Chọn **"Open with Live Server"** (Cổng `5500`) để hưởng thụ trọn vẹn trải nghiệm kết nối AJAX.

---

## 🤝 Đóng góp

Chào mừng bạn đến với dự án! Để đóng góp, vui lòng:
1. Fork repository.
2. Tạo nhánh (`git checkout -b feature/CoolFeature`).
3. Push nhánh đó và bắt đầu Mở Pull Request.



