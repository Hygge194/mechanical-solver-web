### BẢNG ĐẶC TẢ USE-CASE VÀ PHÂN HỆ (MODULES & USE CASES)

Dự án được chia thành 5 Module chính, bao quát các Use-case sau:

#### Module 1: Cho phép người dùng nhập liệu và kiểm tra ngưỡng dữ liệu
*   **UC-02:** Tra cứu động cơ và phân bổ động lực học (M1).

#### Module 2: Thực hiện tính toán theo các chương của khoa KHUD
*   **UC-03:** Thiết kế bộ truyền đai (M2).
*   **UC-04:** Thiết kế bánh răng côn (M3).
*   **UC-05:** Thiết kế bánh răng trụ (M4).

#### Module 3: Cho phép gợi ý linh kiện phù hợp
*   **UC-07:** Gợi ý linh kiện (vòng bi, then, trục) từ Cơ sở dữ liệu.

#### Module 4: Ứng dụng Web/Mobile
*   **UC-01:** Quản lý tài khoản (Đăng ký, Đăng nhập, Đăng xuất).
*   **UC-06:** Lưu chuyển và phục hồi dữ liệu hệ thống (Workflow).
*   **UC-09:** Hiển thị tổng hợp và xuất kết quả báo cáo (PDF).

#### Module 5: Tính năng đặc trưng: sử dụng machine learning
*   **UC-08:** Tối ưu hóa thiết kế và gợi ý thông số bằng Machine Learning.

---

### CHI TIẾT USE-CASE (USE CASE DETAILS)

#### UC-01: Quản lý tài khoản (Đăng ký, Đăng nhập, Đăng xuất)
*   **Use case name:** Đăng ký, đăng nhập và xác thực người dùng.
*   **Actor:** Người dùng.
*   **Description:** Cung cấp cơ chế tạo tài khoản mới, xác thực an toàn bằng JWT Token và quản lý phiên làm việc của người dùng.
*   **Preconditions:** Hệ thống hoạt động bình thường, có kết nối Database.
*   **Normal flow:**
    1. **Đăng ký:** Người dùng nhập thông tin để tạo tài khoản mới. Hệ thống mã hóa mật khẩu bằng Bcrypt và lưu vào CSDL.
    2. **Đăng nhập:** Người dùng nhập Email và Mật khẩu. Hệ thống đối chiếu, nếu đúng thì cấp phát JWT Token và lưu vào trình duyệt.
    3. **Điều hướng:** Hệ thống tự động chuyển người dùng vào trang tính toán (Dashboard).
    4. **Đăng xuất:** Người dùng nhấn đăng xuất, hệ thống xóa Token và đưa về màn hình Login.
*   **Exceptions:**
    *   *Đăng ký lỗi:* Email đã tồn tại trên hệ thống.
    *   *Sai tài khoản/mật khẩu:* Hệ thống từ chối truy cập và báo lỗi trên màn hình.
*   **Postcondition:** Quản lý trọn vẹn vòng đời phiên làm việc của người dùng.

#### UC-02: Tra cứu động cơ và phân bổ động lực học (M1)
*   **Use case name:** Tra cứu động cơ và phân bổ động lực học.
*   **Actor:** Người dùng, Hệ thống.
*   **Description:** Chuẩn hóa dữ liệu đầu vào, tự động gợi ý động cơ phù hợp từ CSDL và tính toán phân bổ các thông số động lực học cho toàn hệ thống.
*   **Preconditions:** Người dùng đã đăng nhập và ở màn hình Module M1.
*   **Normal flow:**
    1. Người dùng nhập các thông số đầu bài (P, n, lực, vận tốc...).
    2. Hệ thống kiểm tra tính hợp lệ và so sánh với ngưỡng thiết kế (TCVN / DB).
    3. Hệ thống tính công suất yêu cầu và truy vấn CSDL để gợi ý Top 3 động cơ phù hợp nhất.
    4. Người dùng chọn 1 động cơ.
    5. Hệ thống tự động phân phối tỉ số truyền tổng và lan truyền thông số ($P, n, T$) lên các trục.
    6. Vẽ biểu đồ động lực học trực quan.
*   **Exceptions:**
    *   *Nhập sai định dạng:* Hệ thống yêu cầu nhập lại.
    *   *Không tìm thấy động cơ:* Hệ thống báo không có động cơ thỏa mãn công suất yêu cầu.
*   **Postcondition:** Bộ thông số động lực học được tính toán hoàn chỉnh, kích hoạt cho các module tiếp theo (M2, M3, M4).

#### UC-03: Thiết kế bộ truyền đai (M2)
*   **Use case name:** Thiết kế bộ truyền đai.
*   **Actor:** Người dùng, Hệ thống.
*   **Description:** Tính toán kích thước, thông số động học và kiểm nghiệm bộ truyền đai hình thang.
*   **Preconditions:** Đã có bộ thông số động lực học từ UC-02.
*   **Normal flow:**
    1. Hệ thống tự động lấy dữ liệu đầu vào từ bảng động lực học.
    2. Người dùng tùy chỉnh thêm tham số (nếu cần).
    3. Hệ thống tính toán loại đai, đường kính bánh đai, khoảng cách trục, và số đai.
    4. Tính toán lực căng đai và lực tác dụng lên trục.
    5. Hiển thị thông số thiết kế chi tiết.
*   **Exceptions:**
    *   *Không đạt điều kiện làm việc:* Cảnh báo đỏ, yêu cầu thay đổi đường kính hoặc loại đai.
*   **Postcondition:** Sinh ra bộ thông số hình học hoàn chỉnh cho bộ truyền đai.

#### UC-04: Thiết kế bánh răng côn (M3)
*   **Use case name:** Thiết kế bánh răng côn.
*   **Actor:** Người dùng, Hệ thống.
*   **Description:** Tính toán thiết kế bộ truyền bánh răng côn và kiểm tra các điều kiện bền.
*   **Preconditions:** Đã có bộ thông số động lực học từ UC-02.
*   **Normal flow:**
    1. Hệ thống lấy dữ liệu đầu vào từ trục tương ứng trong bảng động lực học.
    2. Người dùng chọn vật liệu bánh răng và các hệ số tải trọng.
    3. Hệ thống tính toán kích thước hình học (modul, số răng, đường kính, chiều dài côn).
    4. Kiểm nghiệm độ bền tiếp xúc và độ bền uốn của răng.
    5. Xác định các lực ăn khớp (lực vòng, lực hướng tâm, lực dọc trục).
*   **Exceptions:**
    *   *Không đạt bền tiếp xúc/uốn:* Hệ thống báo lỗi (đỏ), yêu cầu người dùng thay đổi vật liệu hoặc tăng modul, sau đó tính lại.
*   **Postcondition:** Sinh ra bộ thông số kích thước và lực tác dụng cho bánh răng côn.

#### UC-05: Thiết kế bánh răng trụ (M4)
*   **Use case name:** Thiết kế bánh răng trụ.
*   **Actor:** Người dùng, Hệ thống.
*   **Description:** Tính toán thiết kế chi tiết bộ truyền bánh răng trụ (răng thẳng hoặc răng nghiêng) và kiểm nghiệm bền.
*   **Preconditions:** Đã có bộ thông số động lực học từ UC-02.
*   **Normal flow:**
    1. Hệ thống kế thừa dữ liệu đầu vào từ UC-02.
    2. Người dùng cấu hình thông số (loại răng thẳng/nghiêng, vật liệu, hệ số chiều rộng vành răng).
    3. Hệ thống xác định khoảng cách trục, modul, số răng và góc nghiêng (nếu có).
    4. Thực hiện giải bài toán kiểm nghiệm độ bền tiếp xúc và độ bền uốn.
    5. Hiển thị kết quả đạt/không đạt và các chỉ số hình học.
*   **Exceptions:**
    *   *Ứng suất vượt giới hạn:* Hệ thống cảnh báo không đạt, hướng dẫn người dùng điều chỉnh kích thước hoặc vật liệu.
*   **Postcondition:** Có đầy đủ thông số thiết kế bộ truyền bánh răng trụ để xuất bản vẽ.

#### UC-06: Lưu chuyển và phục hồi dữ liệu hệ thống (Workflow)
*   **Use case name:** Lưu chuyển trạng thái tính toán.
*   **Actor:** Hệ thống.
*   **Description:** Tự động lưu trữ các kết quả trung gian từ bước trước và điền sẵn (restore) vào các form ở bước sau để người dùng không phải nhập tay lại.
*   **Preconditions:** Người dùng đã tính toán xong ít nhất một module (VD: M1).
*   **Normal flow:**
    1. Sau khi người dùng tính xong một module, file `workflow.js` thu thập kết quả ($P, n, T, u$).
    2. Lưu trữ dữ liệu ngầm vào `localStorage` của trình duyệt.
    3. Khi người dùng mở tiếp module sau (VD: M2, M3), file `restore.js` được gọi.
    4. Hệ thống tự động đổ (binding) dữ liệu tính toán cũ vào các ô nhập liệu mới.
*   **Exceptions:**
    *   *Người dùng thay đổi thông số cũ:* Hệ thống báo Invalidate, xóa dữ liệu kế thừa và yêu cầu tính lại.
*   **Postcondition:** Đảm bảo luồng dữ liệu tính toán liền mạch, tự động hóa cao.

#### UC-07: Gợi ý linh kiện từ Cơ sở dữ liệu
*   **Use case name:** Gợi ý linh kiện phù hợp (Vòng bi, then...).
*   **Actor:** Hệ thống.
*   **Description:** Dựa trên kết quả tính toán đường kính trục và tải trọng, truy xuất CSDL để đề xuất mã linh kiện tiêu chuẩn.
*   **Preconditions:** Hoàn tất tính toán động lực học và các kích thước trục.
*   **Normal flow:** Hệ thống phân tích lực -> Truy vấn CSDL linh kiện -> Hiển thị danh sách gợi ý.
*   **Postcondition:** Người dùng chọn được linh kiện đạt tiêu chuẩn.

#### UC-08: Tối ưu hóa thiết kế bằng Machine Learning
*   **Use case name:** Tối ưu hóa thiết kế qua AI/ML.
*   **Actor:** Hệ thống.
*   **Description:** Sử dụng mô hình Machine Learning (đã được huấn luyện) để phân tích các bộ thông số đầu vào và gợi ý tỷ số truyền, hoặc kích thước tối ưu nhằm giảm khối lượng hoặc tăng độ bền.
*   **Preconditions:** Tích hợp API Machine Learning vào luồng tính toán.
*   **Normal flow:** Gửi thông số đầu vào tới API AI -> API trả về bộ thông số gợi ý -> Hiển thị cho người dùng đối chiếu.

#### UC-09: Hiển thị tổng hợp và xuất kết quả báo cáo (PDF)
*   **Use case name:** Xuất kết quả báo cáo PDF.
*   **Actor:** Người dùng.
*   **Description:** Tập hợp dữ liệu từ tất cả các module và định dạng thành file báo cáo thuyết minh tính toán.
*   **Preconditions:** Đã hoàn thành tính toán các module.
*   **Normal flow:** Nhấn "Xuất báo cáo" -> Backend gọi thư viện xử lý báo cáo -> Tải file PDF về máy.
