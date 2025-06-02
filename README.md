# SCRAPE_THREADS

#### Bước 1: Mở dự án trong VS Code

#### Bước 2: Đảm bảo Python đã được cài đặt và sẵn sàng
1.  Trong Terminal của VS Code, gõ lệnh sau:
    ```bash
    python3 --version
    ```
2.  Nhấn phím **Enter**. (Cần confirm là python 3)

#### Bước 3: Tạo và Kích hoạt Môi trường Ảo cho Dự án
1.  **Tạo môi trường ảo:**
    Trong Terminal của VS Code, gõ lệnh sau:
    ```bash
    python3 -m venv venv
    ```
    Nhấn phím **Enter**.
    * Lệnh này sẽ tạo một thư mục mới có tên `venv` bên trong thư mục `SCRAPE_THREADS` của bạn. Đây là nơi môi trường ảo được lưu trữ. Quá trình này có thể mất vài giây.

2.  **Kích hoạt môi trường ảo:**
    Trong Terminal của VS Code, gõ lệnh sau:
    ```bash
    source venv/bin/activate
    ```
    Nhấn phím **Enter**.
    * **Quan trọng:** Sau khi chạy lệnh này, bạn sẽ thấy chữ `(venv)` (hoặc một tên tương tự) xuất hiện ở đầu dòng lệnh trong Terminal (ví dụ: `(venv) yourusername@yourMacBook SCRAPE_THREADS %`). Điều này có nghĩa là bạn đã kích hoạt môi trường ảo thành công và mọi lệnh Python/pip bạn gõ từ giờ sẽ chỉ ảnh hưởng đến dự án này.

#### Bước 4: Cài đặt các Thư viện và Công cụ cần thiết
1.  **Cài đặt thư viện Python:**
    Trong Terminal của VS Code (đảm bảo vẫn còn `(venv)` ở đầu dòng lệnh), gõ lệnh sau:
    ```bash
    pip install -r requirements.txt
    ```
    Nhấn phím **Enter**.
    * Lệnh này sẽ tự động tải về và cài đặt tất cả các thư viện Python được liệt kê trong file `requirements.txt` vào môi trường ảo của bạn. Quá trình này có thể mất vài phút tùy thuộc vào tốc độ mạng của bạn.

2.  **Cài đặt các trình duyệt cho Playwright:**
    Thư viện Playwright cần các file trình duyệt thực tế (như Chrome, Firefox) để chạy. Chúng ta cần tải chúng xuống.
    Trong Terminal của VS Code (đảm bảo vẫn còn `(venv)` ở đầu dòng lệnh), gõ lệnh sau:
    ```bash
    playwright install
    ```
    Nhấn phím **Enter**.

#### Bước 5: Chạy Code
python3 crawl_main_posts.py