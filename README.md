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
- Trang con rộng 1200px thay cho 880px; ẩn tiêu đề trang lặp khi nội dung có phần mở đầu riêng; khối chỉ có chữ chia hai cột trên màn hình rộng.
- Không hiện ảnh đại diện của theme khi nội dung trang đã có chính ảnh đó.

## Snippet 39 – Nút tìm kiếm trên đầu trang

Chưa cài lên web: tạo snippet mới trong Code Snippets, dán nội dung file `wordpress/snippets/39-sepa-nut-tim-kiem-dau-trang.php`, chọn chạy ở mọi nơi rồi bật. Tắt snippet để hoàn tác.

- Nút kính lúp ở cuối menu chính; trên điện thoại nằm cạnh nút menu ba gạch.
- Bấm vào mở ô tìm kiếm phủ trên trang, kèm vài từ khoá gợi ý; tìm theo ngôn ngữ đang xem (`/?s=` hoặc `/en/?s=`).
- Phím tắt: `/` hoặc Ctrl+K để mở, Esc để đóng.
