# WineStock

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-blue" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-9146FF" />
  <img src="https://img.shields.io/badge/Docs-MkDocs-green" />
  <img src="https://img.shields.io/badge/Database-SQLite-orange" />
  <img src="https://img.shields.io/badge/Build-PyInstaller-lightgrey" />
</p>

WineStock is a desktop inventory management application designed for small wine shops that need a fast, lightweight, and offline-friendly solution.  
It tracks stock levels, records purchases and sales, generates useful reports, and provides visual alerts when items fall below minimum stock thresholds.

The project focuses strictly on **inventory control**, not accounting or invoicing.

---

## ✨ Features

- Add, edit, delete, and search wines  
- Record stock movements (purchases and sales)  
- Minimum stock alerts and visual indicators
- Clean and modern desktop UI built with CustomTkinter  
- SQLite database with SQLAlchemy ORM  
- Automatic schema migrations powered by Alembic  
- Auto-generated technical documentation using MkDocs + mkdocstrings  
- Fully offline — no cloud services or external dependencies 

---

## 🧰 Tech Stack

- **Python:** 3.12  
- **GUI:** CustomTkinter  
- **Database:** SQLite + SQLAlchemy  
- **Migrations:** Alembic  
- **Docs:** MkDocs + mkdocstrings  
- **Testing:** Pytest  
- **Packaging:** PyInstaller  

---

## 📸 Screenshots

```markdown
![Home Screen](/screenshots/home.png)
![Wine Table](/screenshots/wines.png)
![Edit Wine](/screenshots/wines_edit_.png)
![New Sale](/screenshots/transactions_new_sale.png)
![Reports](/screenshots/reports.png)
```

---

## 🎥 Demo Video

A short walkthrough of the application is available on YouTube:

👉 https://www.youtube.com/xxxxx

The video covers installation, demo data, and the main workflows of the application.

---

## 📦 Installation (Developers)

```bash
git clone https://github.com/emifirmat/wine_stock.git
cd wine_stock

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

> The application supports demo data flags for quick evaluation (see **Running the Application**).

---

## ▶️ Running the Application

```bash
source .venv/bin/activate
python main.py
```

- The database is created automatically on first launch
- Migrations are applied automatically if needed

### Optional startup flags

Start the application with demo wine data:

```bash
python main.py --demo
```

Include demo stock movements (sales and purchases):

```bash
python main.py --demo --with-transactions
```
This populates the database with sample data for testing and exploration.

### Development and production environments

By default, the application runs in **development mode**.

```bash
# Linux / macOS
WINESTOCK_ENV=dev python main.py
```
```bash
# Windows (PowerShell)
$env:WINESTOCK_ENV="dev"
```

You can run in production mode:

```bash
# Linux / macOS
WINESTOCK_ENV=prod python main.py
```
```bash
# Windows (PowerShell)
$env:WINESTOCK_ENV="prod"
python main.py

```

---

## 🗄️ Database & Migrations

The app application **SQLite (`wineshop.db`)**.

- The database file is created automatically if it does not exist
- Schema migrations are applied automatically on application startup.

No manual migration steps are required for end users.

---

## 📚 Documentation

Generate and browse the API documentation locally:

```bash
mkdocs serve
```

Then open:  
**http://127.0.0.1:8000**

---

## 🧪 Tests

Run the test suite:

```bash
pytest tests
```

- Database logic and helper utilities are covered by automated tests
- UI testing is done manually due to CustomTkinter constraints
- Manual UI tests were executed on WSL (Ubuntu) and Windows 11

---

## 🖥️ Packaging (Windows Executable)

Build a standalone executable:

```bash
pyinstaller --noconfirm --onefile --windowed ^
  --hidden-import logging.config ^
  --add-data "assets;assets" ^
  --add-data "alembic.ini;." ^
  --add-data "migrations;migrations" ^
  main.py
```

This executable is intended for distribution.
The repository contains the full reference source code.

---

## 📂 Project Structure

```
wine_stock/
│  main.py          # Application entry point
│  helpers.py       # Utility functions
│  validators.py    # Custom validation logic
│  requirements.txt # Project dependencies
│  mkdocs.yml       # MkDocs configuration
│  alembic.ini      # Alembic configuration for DB migrations
│  README.md        # Project overview and documentation
├─ assets/          # App icons, images, and logos used in the UI
├─ db/              # SQLAlchemy models and database logic
├─ ui/              # CustomTkinter UI components, frames, and styles
├─ migrations/      # Alembic migration files
├─ tests/           # Automated tests (Pytest)
└─ docs/            # MkDocs documentation source
```

---

## 📜 License

This project is shared for **portfolio and educational purposes** only.  
Commercial use or redistribution requires explicit permission.

---

<p align="center">
  Made with ❤️ for learning, building, and improving real-world Python applications.
</p>
