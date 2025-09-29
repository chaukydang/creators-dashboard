Đây là một file **README.md** chuẩn để bạn đưa vào repo và deploy lên Streamlit Cloud. Nó giải thích rõ ràng từ setup local → deploy.

---

```markdown
# 📊 KOL Performance Tracking Dashboard

Dashboard đa trang (multi-page) xây dựng bằng **Streamlit** để phân tích & theo dõi hiệu suất KOL/TikTok Creators.

## 🚀 Tính năng chính
- **Overview:** KPI, phân phối EPV/EP1k, Pareto reach.
- **Leaderboard:** Top KOL theo KOL Score / EPV / EP1k.
- **Country & Segments:** Benchmark theo quốc gia, follower tier.
- **Anomalies:** Phát hiện bất thường (like/view, comment/view, share/view).
- **Export:** Tải dataset đã clean về CSV.
- **Insights:** Lorenz/Gini, decile table, shortlists (Performance-first & Awareness-first), narrative auto-generated.

## 📂 Cấu trúc thư mục
```

app/
├─ App.py                # Entry point Streamlit
├─ utils.py              # Hàm nạp data & helper
├─ requirements.txt      # Danh sách thư viện cần thiết
└─ pages/                # Các trang con của dashboard
├─ 1_Overview.py
├─ 2_Leaderboard.py
├─ 3_Country_Segments.py
├─ 4_Anomalies.py
├─ 5_Export.py
└─ 6_Insights.py
out/
└─ kol_clean.csv         # Dữ liệu clean (output từ script hoặc tải sẵn)
scripts/
└─ kol_cleaner.py        # Script làm sạch dữ liệu raw → clean
data/
└─ tiktok_top_1000.csv   # Dữ liệu raw (có thể bỏ qua khi deploy)

````

## ⚙️ Cài đặt local
Yêu cầu: Python 3.9+  
Khuyên dùng virtualenv:

```bash
git clone https://github.com/<your-username>/creators-dashboard.git
cd creators-dashboard/app

# tạo venv
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# cài gói
pip install -r requirements.txt
````

Chạy local:

```bash
streamlit run App.py
```

Mở trình duyệt tại [http://localhost:8501](http://localhost:8501)

## 🧹 Làm sạch dữ liệu (tùy chọn)

Nếu có raw CSV (`data/tiktok_top_1000.csv`), chạy:

```bash
cd scripts
python kol_cleaner.py
```

File clean sẽ tạo ở `out/kol_clean.csv`.

## ☁️ Deploy lên Streamlit Cloud

1. Push repo lên GitHub (đảm bảo trong repo có `app/` và `requirements.txt`).
2. Vào [https://share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Chọn repo: `<your-username>/creators-dashboard`.
4. Branch: `main`.
5. Main file path: `app/App.py`.
6. Deploy 🎉

👉 Lưu ý:

* Nếu bạn commit `out/kol_clean.csv`, app sẽ chạy ngay.
* Nếu không commit CSV, app sẽ hiển thị uploader → bạn upload file `kol_clean.csv` khi chạy lần đầu.

## 📦 Requirements

```txt
streamlit==1.38.0
pandas
numpy
matplotlib
```

## 📝 Ghi chú

* Nếu file CSV > 50MB, cần Git LFS hoặc đặt file ở ngoài (Google Drive, S3, …) rồi sửa `utils.py` để đọc từ URL.
* Các cảnh báo `DeprecationWarning` đã được xử lý (dùng `np.trapezoid`, `observed=False`, `tick_labels` trong boxplot).
* Có thể mở rộng thêm: export PDF/PPTX, kết nối DB, Google Sheets API để dữ liệu cập nhật realtime.

```

---

Bạn muốn t viết thêm **README tiếng Việt đơn giản cho người không kỹ thuật** (kiểu hướng dẫn sếp mở app trên Streamlit Cloud), hay giữ bản dev-friendly như trên?
```
