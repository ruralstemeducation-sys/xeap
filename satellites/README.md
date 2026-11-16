# Site vệ tinh

Chỉ đăng bài trên **sepa.org.vn**. Các tên miền khác là site tĩnh, tự lấy bài từ sepa rồi đưa lên Cloudflare Pages (miễn phí). Không còn WordPress nào khác cần cập nhật, sao lưu hay vá bảo mật.

```
sepa.org.vn (WordPress, nơi duy nhất đăng bài)
   │  REST API
   ▼
GitHub Actions (2 giờ một lần, hoặc bấm tay) → node satellites/build.mjs
   ▼
Cloudflare Pages: roboticschampionship.vn, darwinstem.vn, …
```

Site vệ tinh chỉ hiện **ảnh, tiêu đề và đoạn tóm tắt**. Bấm vào thì mở bài gốc trên sepa.org.vn, nên Google không bị nội dung trùng lặp và lượt đọc dồn về sepa.

## Bài nào hiện ở site nào

Khai báo trong `sites.json`, mục `filter`. Một bài hiện ở site nếu khớp **bất kỳ** điều kiện nào:

| Khóa | Ý nghĩa |
|---|---|
| `site` | Ô tick **"Hiển thị trên site"** khi viết bài (cần bật snippet 39) |
| `categories` | ID chuyên mục trên sepa |
| `tags` | ID thẻ trên sepa |

Ánh xạ hiện tại (cần xác nhận):

| Site | Lấy từ | Số bài lúc dựng |
|---|---|---|
| roboticschampionship.vn | chuyên mục Robotics (186) + Vietnam National VEX Robotics 2025 (411) | 18 |
| internationalroboticscompetition.vn | chuyên mục Robotics tiếng Anh (204) | 14 |
| roboticsforgood.vn | thẻ ai-for-good (511) | 1 |
| darwinstem.vn | chuyên mục Darwin lab (441) + thẻ darwinstem (443) | 3 |
| stembansacviet.vn | chuyên mục Địa phương (220) | 10 |
| apistem.vn, phuongmyloc.vn | chỉ ô tick "Hiển thị trên site" | 0 |
| sepa.edu.vn | chuyển hướng 301 → sepa.org.vn | |
| internationalroboticscompetition.com.vn | chuyển hướng 301 → internationalroboticscompetition.vn | |

## Nội dung riêng của từng site (tùy chọn)

Tạo thư mục `content/<tên miền>/`:

- `intro.html`: đoạn giới thiệu ngắn dưới tên site ở trang chủ.
- `gioi-thieu.html`: trang `/gioi-thieu/`, menu tự hiện mục "Giới thiệu".
- `_redirects`: chuyển đường dẫn bài cũ trên WordPress sang bài trên sepa, mỗi dòng một cặp:
  ```
  /ten-bai-cu/ https://sepa.org.vn/ten-bai-moi.htm 301
  ```

## Site có giao diện riêng (vd. roboticschampionship.vn)

Nếu có `content/<tên miền>/shell.html` thì site được dựng theo giao diện riêng thay cho mẫu chung:

- `shell.html`: khung trang (header, footer, CSS) với chỗ trống `{{title}}`, `{{description}}`, `{{head}}`, `{{content}}`.
- `pages/<đường-dẫn>.html`: mỗi file là một trang `/<đường-dẫn>/`, riêng `home.html` là trang chủ. Dòng đầu có dạng `<!--meta {"title": "...", "description": "..."} -->`. File có `<!doctype html>` được giữ nguyên, file chỉ có nội dung thì được bọc trong `shell.html`.
- `{{news:6}}` / `{{news:all}}` trong trang: chèn thẻ tin lấy từ sepa theo mẫu `news-card.html`.
- `extra.css`: CSS bổ sung, chèn vào mọi trang.

Muốn sửa nội dung thì sửa thẳng file trong `pages/`. Bản sao lưu WordPress cũ nằm ở `backup/roboticschampionship.vn/`. File `pages-truoc-sua-2026-11-16.json` là bản trước khi sửa lịch, `pages.json` là bản sau khi sửa.

## Chạy thử trên máy

```bash
node satellites/build.mjs
```

```bash
node satellites/build.mjs darwinstem.vn
```

Kết quả nằm ở `satellites/dist/<tên miền>/`.

## Cài đặt lần đầu

1. **Cloudflare**: tạo tài khoản, rồi tạo API token có quyền *Account → Cloudflare Pages → Edit*. Ghi lại Account ID.
2. **GitHub**: vào repo, chọn Settings → Secrets and variables → Actions, thêm `CLOUDFLARE_API_TOKEN` và `CLOUDFLARE_ACCOUNT_ID`.
3. Vào tab Actions, chọn **Site vệ tinh** rồi bấm **Run workflow**. Mỗi tên miền sẽ có một project Pages tên dạng `darwinstem-vn`.
4. Trong từng project Pages: Custom domains, thêm tên miền tương ứng, rồi trỏ DNS theo hướng dẫn của Cloudflare. Nên chuyển nameserver của tên miền về Cloudflare, việc này cũng miễn phí.
5. **Trước khi trỏ DNS**: sao lưu WordPress cũ của site đó và ghi lại các bài đang có lượt truy cập để thêm vào `_redirects`.
6. Bật snippet 39 trên sepa.org.vn để có ô tick "Hiển thị trên site".
