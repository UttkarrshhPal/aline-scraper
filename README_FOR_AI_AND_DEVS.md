# Aline Scraper – Full Context & Setup Guide (For AI & Developers)

## 🚩 Project Purpose
A robust, modular, and scalable content scraper for technical blogs, guides, and PDFs. Designed to extract structured content for Aline's AI tool, supporting dynamic, JS-heavy, and anti-bot sites.

---

## 🏗️ Architecture & What's Implemented

- **Backend:** FastAPI (in `aline-scraper/`)
- **Frontend:** React + TypeScript + Material UI (in `frontend/`)
- **Core Scraper:**
  - `DynamicScraper` (`aline-scraper/app/scraping/dynamic_scraper.py`):
    - Uses Selenium + undetected-chromedriver for all scraping
    - Handles JS rendering, infinite scroll, hash navigation, and robust link/content extraction
    - Multi-strategy content extraction (trafilatura, newspaper3k, BeautifulSoup)
  - `BlogScraper` now delegates all work to `DynamicScraper`
- **PDF Extraction:** `/scrape/pdf` endpoint, works with file upload
- **API Endpoints:** `/scrape`, `/scrape/{job_id}/status`, `/scrape/{job_id}/results`, `/scrape/pdf`
- **Frontend UI:** Multi-tab, user-friendly, with clear instructions for each endpoint

---

## 📝 What's Left / Next Steps
- Test and debug on your new machine (Windows recommended for Selenium stability)
- If needed, refactor `GuideCollectionScraper` to use `DynamicScraper`
- Ensure ChromeDriver and Chrome are compatible on your system
- Continue testing on all required URLs

---

## ⚡ Setup Instructions (Windows)

### 1. Install Python 3.9+ and Node.js (for frontend)
- [Python Download](https://www.python.org/downloads/)
- [Node.js Download](https://nodejs.org/)

### 2. Install Google Chrome
- [Chrome Download](https://www.google.com/chrome/)

### 3. Clone the Repo
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 4. Set Up Python Environment
```bash
python -m venv venv
venv\Scripts\activate  # (Windows)
pip install --upgrade pip
pip install -r aline-scraper/requirements.txt
```

### 5. Install ChromeDriver (if needed)
- Download the correct ChromeDriver for your Chrome version and Windows architecture:  
  [ChromeDriver Download](https://googlechromelabs.github.io/chrome-for-testing/#stable)
- Unzip and place the `chromedriver.exe` somewhere on your PATH, or note its location.

### 6. Configure DynamicScraper to Use Your ChromeDriver
- In `aline-scraper/app/scraping/dynamic_scraper.py`, update the `__init__`:
  ```python
  self.driver = uc.Chrome(options=options, driver_executable_path='C:/path/to/chromedriver.exe')
  ```
  Replace with your actual path.

### 7. Start the Backend
```bash
cd aline-scraper
PYTHONPATH=. python -m uvicorn app.main:app --reload --port 8000
```

### 8. Start the Frontend
```bash
cd frontend
npm install
npm run dev
```
- Open the URL shown (e.g., http://localhost:5173)

---

## 🧪 Testing
- Use the frontend to test all required URLs (see below).
- Watch backend logs for errors.
- If you get a "network error," check backend logs for Selenium/ChromeDriver issues.

---

## 🔗 Required Test URLs
- https://realpython.com/
- https://interviewing.io/learn#interview-guides
- https://interviewing.io/topics#companies
- https://www.geeksforgeeks.org/tag/interview-experiences/
- https://nilmamano.com/blog/category/dsa
- https://overreacted.io/

---

## 🛠️ Troubleshooting
- **ChromeDriver errors:**
  - Make sure ChromeDriver matches your Chrome version and CPU architecture.
  - Set the correct path in `DynamicScraper`.
- **Python package errors:**
  - Run `pip install -r aline-scraper/requirements.txt` again.
- **Frontend issues:**
  - Make sure Node.js is installed and run `npm install` in `/frontend`.
- **Mac-specific undetected_chromedriver error:**
  - If you see `OSError: [Errno 86] Bad CPU type in executable`, the downloaded binary is not compatible with your Mac's CPU. This is why Windows is recommended for Selenium scraping.
  - On Windows, this issue should not occur if you use the correct ChromeDriver.

---

## 🧠 What's Already Done (for AI/Developer Context)
- All scraping logic is now routed through `DynamicScraper` (Selenium + undetected-chromedriver)
- BlogScraper is refactored; GuideCollectionScraper may still need update
- PDF and API endpoints are working
- Frontend is ready and user-friendly
- All code is modular and ready for further extension

---

## 🚦 How to Continue
- If you see any errors, paste the logs here for immediate debugging.
- If you want to add new features (e.g., more robust guide scraping, deduplication, etc.), just describe them and continue from here.

---

**This file gives full context for any AI or developer to pick up exactly where you left off. Just open this repo on your new machine, follow the steps above, and you're ready to go!** 