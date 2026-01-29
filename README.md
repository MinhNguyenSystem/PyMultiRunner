# 🐍 PyMultiRunner - Python Multi-Version Interactive TUI

> **Chạy, kiểm thử và tương tác với script Python trên nhiều phiên bản cùng một lúc.**

**PyMultiRunner** là một công cụ dòng lệnh (CLI) mạnh mẽ dành cho **Linux/macOS**, giúp các nhà phát triển Python kiểm tra độ tương thích của mã nguồn trên nhiều trình thông dịch (Python 3.8, 3.9, 3.10, 3.11, 3.12...) song song trong thời gian thực.

Được xây dựng dựa trên thư viện [Textual/Rich](https://github.com/Textualize/rich), công cụ mang lại giao diện terminal đẹp mắt, hỗ trợ tương tác Shell (REPL) và quản lý tiến trình thông minh.

---

## 📸 Demo

### 1. Giao diện chạy đa phiên bản (Split-Pane View)
Hiển thị song song output, hỗ trợ màu sắc cú pháp và trạng thái tiến trình.
![Running Interface](https://sf-static.upanhlaylink.com/img/image_202601308d70a6a3d01328f271b574c58710de28.jpg)

### 2. Menu chọn phiên bản
Tự động quét và cho phép bật/tắt các phiên bản Python tìm thấy trong hệ thống.
![Menu Version](https://sf-static.upanhlaylink.com/img/image_2026013017ebdaf80d4df8e234d7b75243802f3b.jpg)

---

## ✨ Tính Năng Nổi Bật

*   **🕵️ Tự động dò tìm (Auto-Discovery):** Quét biến môi trường `PATH` để tìm tất cả các file thực thi `python*` đã cài đặt và lấy phiên bản cụ thể.
*   **🖥️ Giao diện TUI trực quan:** Sử dụng `Rich` để chia màn hình thành các panel, tự động thay đổi kích thước dựa trên số lượng phiên bản đang chạy.
*   **🕹️ Hỗ trợ PTY (Pseudo-Terminal):**
    *   Chạy script như trong terminal thật (hỗ trợ màu sắc, con trỏ).
    *   Hỗ trợ **Interactive Shell** (REPL) `>>>`.
    *   Xử lý tốt các lệnh `input()`, `getpass()`.
*   **⚡ Auto-Focus thông minh:** Tự động phát hiện khi chương trình dừng chờ nhập liệu (dựa trên Regex prompt như `input:`, `choose:`, `y/n`) và chuyển con trỏ bàn phím sang panel đó.
*   **📡 Broadcast Input (Gửi tất cả):** Tính năng cho phép gõ một lệnh và gửi đồng thời đến tất cả các phiên bản đang chạy (rất hữu ích để test nhanh).
*   **📊 Thông số chi tiết:** Hiển thị thời gian chạy, mã thoát (Exit code), chế độ Shell.

---

## 🛠️ Yêu Cầu & Cài Đặt

### Yêu cầu hệ thống
*   **Hệ điều hành:** Linux hoặc macOS.
    *   *(Không hỗ trợ Windows gốc do sử dụng thư viện `pty`, `termios`, `fcntl`)*.
*   **Python:** Python 3.x làm trình khởi chạy.

### Cài đặt thư viện phụ thuộc
Bạn cần cài đặt các thư viện cần thiết trước khi chạy:

```bash
pip install rich colorama
🚀 Hướng Dẫn Sử Dụng
1. Khởi chạy

Bạn có thể chạy tool và chọn file từ danh sách, hoặc chỉ định file ngay từ đầu:

# Cách 1: Chọn file từ giao diện
python runner.py

# Cách 2: Chỉ định file script cần test
python runner.py my_script.py
2. Menu Cấu Hình

Khi khởi động, tool sẽ liệt kê các phiên bản Python tìm thấy.

Nhập số thứ tự (ví dụ 1, 3) để Bật/Tắt phiên bản đó.

Nhập R để bắt đầu chạy.

Nhập K để thoát.

🎮 Các Phím Điều Khiển (Shortcuts)

Trong quá trình chạy (Runtime), sử dụng các phím sau để điều khiển:

Phím Tắt	Chức Năng
Alt + 1..9	Chuyển tiêu điểm (Focus) nhanh đến panel tương ứng (Panel 1, 2, 3...).
Ctrl + T	Send ALL Mode: Lệnh bạn nhập tiếp theo sẽ được gửi tới tất cả các panel (Dùng để nhập input giống nhau).
Ctrl + O	Mở Menu Lệnh Phụ: <br> - q: Thoát chương trình (Force Kill). <br> - r: Bật/Tắt chế độ RAW input. <br> - 1-9: Chuyển focus.
Ctrl + C	Thoát chương trình ngay lập tức.
Nhập liệu thường	Gửi ký tự đến panel đang được Focus (có viền màu xanh lá hoặc xanh dương).
📝 Cơ Chế Hoạt Động (Technical)

Process Management: Script sử dụng subprocess.Popen kết hợp với os.openpty() để tạo ra các tiến trình con giả lập terminal. Điều này cho phép bắt được cả stdout và stderr mà không bị buffer (đệm), đồng thời cho phép gửi stdin vào như thật.

Non-blocking I/O: Sử dụng select.select() để lắng nghe dữ liệu từ Master FD (File Descriptor) của các tiến trình con và từ bàn phím người dùng trên cùng một luồng chính.

UI Rendering: rich.live.Live được dùng để vẽ lại giao diện liên tục (20 FPS). Output từ các tiến trình được lưu vào deque (bộ đệm vòng) để tránh tràn bộ nhớ hiển thị.

⚠️ Lưu ý

Chương trình được thiết kế chủ yếu cho môi trường dòng lệnh (CLI).

Nếu script mục tiêu của bạn sinh ra quá nhiều output (hàng ngàn dòng/giây), giao diện có thể bị lag nhẹ do việc vẽ lại UI của terminal.

Made with ❤️ by MinhNguyen2412
