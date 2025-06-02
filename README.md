# SCRAPE_THREADS - Social Media Crawler

## Hướng dẫn Cài đặt và Chạy

### Bước 1: Mở dự án trong VS Code
1. Mở VS Code
2. Chọn **File** → **Open Folder** 
3. Chọn thư mục `social`

### Bước 2: Cài đặt Python và thư viện
1. **Kiểm tra Python:**
   ```bash
   python --version
   ```

2. **Tạo môi trường ảo:**
   ```bash
   python -m venv venv
   ```

3. **Kích hoạt môi trường ảo:**
   
   **Trên Windows:**
   ```bash
   venv\Scripts\activate
   ```
   
   **Trên macOS/Linux:**
   ```bash
   source venv/bin/activate
   ```
   
   (Sẽ thấy `(venv)` xuất hiện ở đầu dòng lệnh)

4. **Cài đặt thư viện:**
   ```bash
   pip install -r requirements.txt
   ```


### Bước 3: Chạy ứng dụng
```bash
python app.py
```

Sau đó mở trình duyệt và truy cập: **http://localhost:5000**

---

## Chức năng
- **Topic Crawl:** Tìm kiếm bài viết theo từ khóa
- **Users Crawl:** Thu thập dữ liệu người dùng theo username  
- **View Data:** Xem dữ liệu đã thu thập
- **Download:** Tải xuống file dữ liệu