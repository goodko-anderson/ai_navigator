import os

# 為了避免複製時格式被聊天視窗切斷，我們用 Python 變數來組裝這些符號
# 這樣您複製時就絕對不會斷掉了！
tick = "`" * 3
bash_block = tick + "bash"
ini_block = tick + "ini"
text_block = tick + "text"
end_block = tick

# 這是完整的 README 內容
content = f"""# 🚀 AI Navigator (AI 領航員)

> 基於 Django 與 Google Gemini 2.0 建構的全方位 AI 實驗平台。整合文字生成、視覺逆向工程與專業數據分析工具。

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.0-orange?logo=google)
![Pandas](https://img.shields.io/badge/Data-Pandas-150458?logo=pandas)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 📖 專案簡介 (Introduction)

**AI Navigator** 是一個整合多種 AI 應用場景的 Web 平台。它不僅僅是一個聊天機器人，更是一個生產力工具箱。專案利用 Google 最新的 **Gemini 2.0 Flash** 模型，實現了從「文章自動撰寫」到「圖片風格逆向分析」的功能，並內建了符合 **ISO 11608** 標準的醫療級劑量準確度分析工具。

本專案展示了如何將大型語言模型 (LLM) 與傳統 Web 框架 (Django) 以及科學運算庫 (NumPy/Pandas) 進行深度整合。

## ✨ 核心功能 (Key Features)

### 1. ✍️ AI 智慧寫手 (AI Writer)
* **一鍵生成**：輸入主題，自動生成結構完整的 HTML 教學文章。
* **智慧排版**：自動處理標題 (H2/H3)、清單與程式碼區塊。
* **自動關聯**：AI 會自動分析內容，將文章與系統內的相關工具 (Tools) 進行資料庫關聯。
* **SEO 優化**：支援繁體中文 URL Slug 自動生成與防撞機制。

### 2. 👁️ 視覺逆向工程 (Image Reverse Engineering)
* **以圖生文**：上傳圖片，利用 Gemini Vision 分析其構圖、光影與藝術風格。
* **Prompt 生成**：自動產出適用於 Midjourney 的英文咒語 (Prompts)，協助使用者複製風格。

### 3. 📊 ISO 11608 劑量分析儀 (Dose Accuracy Analysis)
* **專業統計**：針對醫療器材數據進行 **Anderson-Darling 常態性檢定**。
* **視覺化報表**：使用 Matplotlib 自動繪製直方圖 (Histogram) 與機率圖 (Probability Plot)。
* **演算法實作**：完整實作 ISO 規範的大小劑量容許誤差 (Fixed/Percent) 計算邏輯。

## 🛠️ 技術堆疊 (Tech Stack)

* **後端框架**: Django 5.x
* **AI 模型**: Google Gemini API (gemini-2.0-flash / gemini-1.5-pro)
* **資料分析**: Pandas, NumPy, SciPy
* **資料視覺化**: Matplotlib (Agg backend)
* **資料庫**: SQLite (開發環境) / PostgreSQL (生產環境相容)
* **前端**: HTML5, CSS3, Bootstrap 5

## 🚀 快速開始 (Quick Start)

請依照以下步驟在您的本機環境執行此專案：

### 1. 複製專案 (Clone)
{bash_block}
git clone [https://github.com/goodko-anderson/ai_navigator.git](https://github.com/goodko-anderson/ai_navigator.git)
cd ai_navigator
{end_block}

### 2. 建立虛擬環境 (Virtual Environment)
{bash_block}
# Windows
python -m venv venv
venv\\Scripts\\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
{end_block}

### 3. 安裝依賴套件 (Install Dependencies)
{bash_block}
pip install -r requirements.txt
{end_block}

### 4. 設定環境變數 (.env)
請在專案根目錄建立 `.env` 檔案，並填入您的 Google API Key：
{ini_block}
# .env
GEMINI_API_KEY=您的_Google_AI_Studio_Key_請勿外流
DEBUG=True
SECRET_KEY=您的DjangoSecretKey
{end_block}

### 5. 資料庫遷移與啟動 (Migrate & Run)
{bash_block}
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
{end_block}

現在，打開瀏覽器前往 `http://127.0.0.1:8000/` 即可開始使用！

## 📂 專案結構 (Project Structure)

{text_block}
ai_navigator/
├── core/               # 核心應用 (首頁、共用邏輯)
├── labs/               # AI 實驗室 (寫手、逆向工程、ISO 分析)
├── tools/              # 工具展示與管理
├── tutorials/          # 文章發布系統
├── media/              # 使用者上傳檔案 (不計入 Git)
├── templates/          # HTML 模板
├── static/             # CSS/JS 靜態檔案
├── manage.py           # Django 管理腳本
└── requirements.txt    # 套件清單
{end_block}

## 🤝 聯絡作者 (Contact)

* **Developer**: Anderson Lee
* **GitHub**: [goodko-anderson](https://github.com/goodko-anderson)

---
*Created with ❤️ by Anderson Lee*
"""

# 將內容寫入 README.md
with open("README.md", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ 成功！README.md 已自動生成，格式絕對完美。")