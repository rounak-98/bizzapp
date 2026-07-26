# BizApp 💼 - Online Quotation & Invoice Maker

Professional Django online Quotation and Tax Invoice Maker app with document status tracking, custom line-item pricing, 1-click quote-to-invoice conversion, printable A4 PDF layouts, GST breakdown, company branding, and analytics.

---

## ✨ Features
- 🧾 **Professional Quotations**: Custom quote numbering (`QTN-2026-0001`), status tracking (`Draft`, `Sent`, `Accepted`, `Rejected`, `Expired`, `Converted`), validity dates, line pricing overrides, and unit discounts.
- ⚡ **1-Click Quote-to-Invoice Conversion**: Instantly convert accepted proposals into official Tax Invoices with copied line items.
- 📑 **Printable A4 PDF Layouts**: Clean `@media print` styling for Quotation proposals, Tax Invoices, and Performa advance receipts with company logo, bank details, and signature blocks.
- 👥 **Customer & Inventory Directory**: Manage customer details, products/services, standard pricing, and units.
- 🏢 **Company Branding & Payment Setup**: Custom company logo, GSTIN, bank account numbers, IFSC, UPI ID, and signatory titles.
- 📊 **Dashboard & Financial Analytics**: Real-time proposal metrics cards, revenue tracking (paid vs pending balance), search, and status filters.
- 🧪 **Unit Test Suite**: Automated verification for quote calculations, tax splitting, and status transitions.

---

## ⚙️ Tech Stack
- **Backend:** Django 6.0.1 (Python 3.13)
- **Database:** MySQL (via `mysqlclient`)
- **Frontend:** HTML5, Modern Glassmorphic CSS, JavaScript
- **Environment:** Virtualenv on Windows

---

## 🚀 Quick Setup (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

Run tests:
```powershell
.\.venv\Scripts\python.exe manage.py test core
```

---

👤 **Author**: Rounak Pathak  
📧 **Email**: ronakpathak9080@gmail.com
