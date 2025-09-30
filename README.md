# 📊 KOL Performance Tracking Dashboard

Dashboard đa trang (multi-page) xây dựng bằng **Streamlit** để phân tích & theo dõi hiệu suất KOL/TikTok Creators.

## 🚀 Tính năng
- **Overview:** KPI, phân phối EPV/EP1k, **Pareto reach** (tập trung reach).
- **Leaderboard:** Lọc/tìm kiếm, xếp hạng theo **KOL Score / EPV / EP1k**.
- **Country & Segments:** Benchmark theo **quốc gia** và **follower tier**.
- **Anomalies:** Phát hiện bất thường **like/view, comment/view, share/view**.
- **Export:** Tải dữ liệu đã clean (CSV).
- **Insights:** **Lorenz/Gini**, **decile table**, **shortlists** (Performance-first & Awareness-first), **narrative** auto.

---

## 📂 Cấu trúc thư mục

```text
app/
├─ App.py                 # Entry point Streamlit
├─ utils.py               # Hàm nạp data & helper
├─ requirements.txt       # Danh sách thư viện
└─ pages/                 # Các trang con
   ├─ 1_Overview.py
   ├─ 2_Leaderboard.py
   ├─ 3_Country_Segments.py
   ├─ 4_Anomalies.py
   ├─ 5_Export.py
   └─ 6_Insights.py
scripts/
└─ kol_cleaner.py         # Script làm sạch dữ liệu raw → clean
out/
└─ kol_clean.csv          # Dữ liệu clean (có thể commit để chạy ngay)
data/
└─ tiktok_top_1000.csv    # Dữ liệu raw (không bắt buộc commit)
```

> Bạn có thể **commit `out/kol_clean.csv`** để app chạy ngay, hoặc dùng **uploader** trong app để upload CSV khi chạy lần đầu.

---

## ⚙️ Cài đặt & chạy local

Yêu cầu: **Python 3.9+**. Khuyến nghị virtualenv.

```bash
git clone https://github.com/<your-username>/creators-dashboard.git
cd creators-dashboard/app

# tạo & kích hoạt venv
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# cài thư viện
pip install -r requirements.txt

# chạy app
streamlit run App.py
```

Mở trình duyệt: http://localhost:8501

---

## 🧹 Làm sạch dữ liệu (tùy chọn)

Nếu bạn có file raw `data/tiktok_top_1000.csv`, tạo file clean:

```bash
cd scripts
python kol_cleaner.py
```

File clean sẽ được tạo ở `out/kol_clean.csv`.

---

## ☁️ Deploy lên Streamlit Cloud

1. Push repo lên GitHub (đảm bảo có `app/` và `app/requirements.txt`).  
2. Truy cập https://share.streamlit.io → **New app**.  
3. Chọn repo: `<your-username>/creators-dashboard`.  
4. Branch: `main`.  
5. **Main file path**: `app/App.py`.  
6. Bấm **Deploy** 🎉

**Lưu ý:**
- Nếu **commit `out/kol_clean.csv`**, app chạy ngay.
- Nếu **không commit CSV**, lần đầu mở app sẽ có **file uploader** → upload `kol_clean.csv` rồi ấn **Rerun**.

---

## 📦 Requirements

```txt
streamlit==1.38.0
pandas
numpy
matplotlib
```

> Nếu thêm thư viện mới, cập nhật file `app/requirements.txt` rồi `git push` để Cloud tự rebuild.

---

## 🧠 Gợi ý sử dụng

- **Awareness campaign**: ưu tiên **Macro/Mega** (reach lớn), kèm guardrail `like/view` để tránh reach “rỗng”.  
- **Performance campaign**: ưu tiên **Micro/Mid** có **EPV** & **EP1k** cao (xem trang **Insights** và **shortlists**).  
- **Chống rủi ro**: kiểm tra mục **Anomalies** để loại KOL có tỷ lệ tương tác bất thường.

---

## 📑 Data Dictionary (kol_clean.csv)

| Column                       | Type    | Description                                                   |
|-----------------------------|---------|---------------------------------------------------------------|
| account                     | str     | Tên tài khoản / channel                                      |
| country                     | str     | Quốc gia (nếu có)                                            |
| followers                   | int     | Số follower                                                   |
| views_avg                   | float   | Lượt xem trung bình/clip                                     |
| likes_avg                   | float   | Lượt like trung bình/clip                                    |
| comments_avg                | float   | Lượt comment trung bình/clip                                 |
| shares_avg                  | float   | Lượt share trung bình/clip                                   |
| engagement_per_view (EPV)   | float   | (likes+comments+shares)/views_avg                             |
| engagement_per_1k_followers | float   | (likes+comments+shares)/(followers/1000)                      |
| kol_score                   | float   | Điểm tổng hợp 0..1 (theo config.yaml, robust scaled)          |
| follower_tier               | str     | Tier phân theo followers (Micro/Medium/Macro/Mega)           |

> Công thức & trọng số có thể chỉnh trong `app/config.yaml`.

## 🛠️ Troubleshooting

- **`FileNotFoundError: kol_clean.csv`**  
  - Commit `out/kol_clean.csv` vào repo **hoặc** dùng uploader trong app để upload CSV khi chạy.

- **Thiếu thư viện / `ModuleNotFoundError`**  
  - Thêm tên gói vào `app/requirements.txt`, commit & push lại.

- **CSV > 50MB**  
  - Dùng **Git LFS** (`git lfs install && git lfs track "*.csv"`) **hoặc** lưu CSV ngoài (GDrive/S3/URL) và sửa `utils.py` để đọc từ URL.

- **Cảnh báo Deprecation**  
  - Repo này đã cập nhật: dùng `np.trapezoid`, `observed=False` trong `groupby`, `tick_labels` với `boxplot`.

- **ModuleNotFoundError: app**  
  Đảm bảo ở đầu `app/App.py` và mỗi `app/pages/*.py` có bootstrap:
  ```python
  import os, sys
  ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
  if ROOT not in sys.path:
      sys.path.insert(0, ROOT)
  try:
      from app import utils as U  # noqa: E402
  except ModuleNotFoundError:
      import utils as U           # noqa: E402

---

## 🔒 Secrets (tuỳ chọn)

Nếu cần đọc dữ liệu từ Google Sheets/DB, đặt thông tin trong **Secrets** của Streamlit Cloud (Manage app → Settings → Secrets). Trong code, truy cập bằng `st.secrets["KEY"]`.

---

## 📜 License

Thêm `LICENSE` nếu bạn muốn chia sẻ public/open-source.

---

**Made with ❤️ & Streamlit.**  
Mọi góp ý / PR hoan nghênh!
