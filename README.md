# UniCross 115：跨校系全能查榜助手 🎓
**UniCross 115** 是一個專為 115 學年度大學申請入學開發的高效能查榜工具。它打破了傳統官方查詢系統的限制，整合了「普通大學 (CAC)」與「科技校院 (JCTV)」兩大體系，並獨家內建了全台考場全銜對照與姓名自動關連功能。
---

https://potatosserver.github.io/UniCross-115/


## 🌟 核心特色

-   **🔗 跨系統整合**：同時抓取普大申請入學與科大四年制申請的一階篩選名單。
-   **⚡ 高速同步**：採用多執行緒（Multi-threading）技術，支援 15+ 併發連線，全台名單同步僅需數十秒。
-   **📛 姓名自動連動**：利用科大名單特質，自動建立應試號碼與姓名的對照表，讓普大名單也能顯示考生姓名。
-   **📍 考場全銜對照**：精準收錄 115 學年度學測試場分配表，查詢號碼即刻顯示「臺北市立中山女高」等完整全銜。
-   **🖥️ 雙查詢模式**：提供終端機（Terminal）互動式查詢與美化的網頁版（HTML/JS）查詢介面。
-   **☁️ 雲端支援**：支援從 GitHub 下載預爬好的資料庫，免去設定 Cookie 的煩惱。

## 🛠️ 技術棧

-   **Backend**: Python (Requests, BeautifulSoup4, tqdm, ThreadPoolExecutor)
-   **Frontend**: HTML5, JavaScript (ES6+), Tailwind CSS
-   **Data**: JSON (Standardized Schema)

## 📂 檔案結構

-   `corss.py`: Python 核心程式，負責數據同步、本地查詢及 JSON 匯出。
-   `index.html`: 網頁版查詢介面，具備校系交叉查詢與考場顯示功能。
-   `exam_local_db.json`: 爬取後產出的標準化數據庫。

## 🚀 快速開始

### 1. 安裝環境需求
確保電腦已安裝 Python 3.8 或以上版本，並安裝必要套件：
```bash
pip install requests beautifulsoup4 tqdm
```

### 2. 資料同步 (模式 1)
當載入失敗且需要獲取最新的官網資料：
1.  手動進入[科技校院查詢系統](https://ent01.jctv.ntut.edu.tw/applys1result/college.html)。
2.  按 F12 打開開發者工具，從 `Cookie` 中複製 `JSESSIONID` 的值。
3.  將該值填入 `corss.py` 內的 `JCTV_COOKIES` 變數。
4.  執行程式並選擇模式 `1`：
    ```bash
    python corss.py
    ```

### 3. 啟動查詢
-   **本地查詢**：同步完成後直接在終端機輸入號碼或姓名進行搜尋。
-   **網頁查詢**：直接用瀏覽器開啟 `index.html`，並確保 `exam_local_db.json` 位於同一目錄。

## 🔍 查詢說明

-   **應試號碼查詢**：輸入 8 位數字准考證號碼。
-   **姓名查詢**：輸入考生全名（如：葉學群），系統將自動轉換為官網遮蓋格式（葉Ｏ群）進行匹配，並列出所有可能的錄取校系。

## ⚠️ 免責聲明

1. 本專案僅供學術交流與個人便利查詢使用，抓取之資料版權歸「大學甄選入學委員會」與「技專校院招生委員會聯合會」所有。
2. 查榜結果請以官方正式公告為準。
3. 請勿用於任何商業用途或對目標網站進行惡意攻擊。

## 🤝 貢獻
歡迎提交 Pull Request 或回報 Issue。

---
**UniCross 115** - 助考生在 115 申請季一臂之力！
