# BizApp 💼

Minimal Django invoicing/quotation app with GST breakdown, customer management, and a professional admin dashboard.

---

## ✨ Features
- 🧾 Generate quotations and invoices with CGST/SGST calculations
- 👥 Manage customers, items, and company info
- 📊 View and print detailed financial documents
- 🎨 Glassmorphic UI with modular templates
- 🔐 Secure admin panel with superuser access
- 🧪 Built-in testing and linting tools

---

## ⚙️ Tech Stack
- **Backend:** Django 6.0.1 (Python 3.13)
- **Database:** MySQL (via `mysqlclient`)
- **Frontend:** HTML, CSS, JavaScript
- **Environment:** Virtualenv on Windows

---

## 🚀 Setup (Windows PowerShell)

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # fill in values
python manage.py migrate
python manage.py runserver

Run tests:

```powershell
python manage.py test
```

Run linters / formatters:

```powershell
.\.venv\Scripts\python.exe -m isort .
.\.venv\Scripts\python.exe -m black .
.\.venv\Scripts\python.exe -m flake8 .
```

Notes:
- Keep `SECRET_KEY` and DB credentials in environment variables or a secret manager.
- Use `.env.example` as a template; don't commit `.env`.
👤 Author
Rounak Pathak
📧 ronakpathak9080@gmail.com

---

👉 Copy this into your `README.md`, commit it, and push:
```powershell
git add README.md
git commit -m "Update README with full project overview"
git push
