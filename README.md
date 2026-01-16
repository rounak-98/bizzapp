# BizApp

Minimal Django invoicing/quotation app.

Setup (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env # fill values
python manage.py migrate
python manage.py runserver
```

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
