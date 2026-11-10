# xeap – website SEPA (sepa.org.vn)

Repo dùng để xây lại và quản lý thay đổi cho website của Liên minh Thúc đẩy Giáo dục STEM (SEPA).

## Nội dung

- `docs/ra-soat-2026-11/` – báo cáo rà soát toàn diện website (11/2026), kèm ảnh chụp.
- `wordpress/snippets/` – bản sao mã các snippet đang chạy trên WordPress (plugin Code Snippets).
  Số ở đầu tên file là ID snippet trên web. Sửa trên web thì cập nhật lại file ở đây.

## Snippet 38 – Sửa nhanh sau rà soát

Đang bật trên sepa.org.vn. Tắt snippet để hoàn tác toàn bộ:

- Ẩn danh sách tài khoản (REST `/wp/v2/users`, sitemap users, trang tác giả) với khách chưa đăng nhập.
- Header bảo mật: HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy; bỏ `X-Powered-By`.
- Tiêu đề trang dạng `Tên trang | SEPA`.
- Chuyển hướng 301 các trang trùng/rỗng.
- Canonical cho trang chủ và trang chuyên mục (kể cả trang 2, 3…), meta description cho trang chuyên mục, dữ liệu cấu trúc Organization.
- Trang chủ: một thẻ H1, khu "Kết nối cùng SEPA" gọn.
- Sửa độ tương phản trang `/sang-lap`.
