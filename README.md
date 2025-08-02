# 🏛️ Court-Data Fetcher & Mini-Dashboard

A web-based utility to **fetch court case order details** from the High Court of Delhi and display them in a clean, paginated dashboard format. Built using **Flask**, **Selenium**, and **SQLite** with support for **error handling**, **flash messaging**, and (optionally) **Docker** deployment.

---

## 📍 Court Covered
- **High Court of Delhi**

---

## 📌 Features

- 🔍 Search case by number (e.g. `W.P.(C) - 4781 - 2025`)
- 📄 View all available order links (title + date)
- 📥 Download order PDFs directly from UI
- ⚠️ Flash messages for user feedback and errors
- 🧱 Robust error handling (timeouts, unexpected HTML, invalid inputs, etc.)
- 🔄 Pagination for large number of orders (50+)
- 🐳 Docker support (optional)
- 🧪 Basic unit test structure (optional)
- ✅ Optional CI workflow integration (GitHub Actions ready)

---

## ⚙️ Setup Instructions

### 1. Clone this repository
```bash
git clone https://github.com/your-username/court-data-fetcher.git
cd court-data-fetcher
```

### 2. Create & activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # on Windows use venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set environment variables 
```bash
export FLASK_APP=driver.py
export FLASK_ENV=development
```
### Optional: Create a `.env` file with:
```bash
SECRET_KEY=your_secret_key
DATABASE_URI=sqlite:///your_db_file.db
```

### 5. Run the Flask app
```bash
flask run
```

---

## 🧪 Sample Case Numbers to Try

You can test the dashboard with these:
- `W.P.(C) - 4781 - 2025`
- `W.P.(C) - 9972 - 2024`
- `CS(OS) - 524 - 2024`

---
## 🤖CAPTCHA Solving Strategy
- The Delhi High Court website uses a CAPTCHA displayed as readable text on the page.
- The scraper extracts this text directly from the webpage’s DOM.
- This extracted text is automatically entered into the CAPTCHA input field before form submission.
- This method bypasses the need for complex OCR or third-party CAPTCHA solving services.
- **Note:** If the website updates their CAPTCHA to an image or other mechanism, this strategy will require modification.


## 🐳 Docker Support 

### Build the Docker image
```bash
docker build -t court-scraper .
```

### Run the container
```bash
docker run -p 5000:5000 court-scraper
```

---

## 🧪 Testing 

Unit tests are placed in `test_app.py` file. To run them:
```bash
pytest test_app.py
```

(Current test coverage includes form input validation, basic route checks, and scraper mock logic.)

---

## 📂 Folder Structure

```
.
├── driver.py            # Main Flask application
├── scraper.py           # Scraper logic
├── case_data.py         # Dropdown options for case types and years
├── templates/           # Jinja2 templates (HTML)
├── static/              # CSS/JS
├── tests/               # Test cases (optional)
├── requirements.txt     # Dependencies
├── Dockerfile           # Container build file (optional)
└── README.md
```

---

## ⚠️ Edge Case Handling

| Scenario                        | Handling |
|---------------------------------|----------|
| Invalid or empty case number    | Flash warning |
| Network errors / timeouts       | Graceful fallback + user alert |
| Unexpected HTML format          | Logged internally, user warned |
| No orders found                 | Flash message shown |
| JavaScript disabled             | HTML validation + graceful form fallback |

---

## 📄 License

MIT – Free to use and modify.

---
