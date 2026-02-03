# KOL Performance Tracking Dashboard

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
---


---

**Made with ❤️ & Streamlit.**  
Mọi góp ý / PR hoan nghênh!
