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
- Minimum stock alerts  
- Clean and modern UI using CustomTkinter  
- SQLite database with SQLAlchemy ORM  
- Alembic-powered migrations  
- Auto-generated API documentation using MkDocs + mkdocstrings  
- Fully offline — no cloud dependencies  

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

Screenshots will be added later.

Example format:
```markdown
![Home Screen](/screenshots/home.png)
![Wine Table](/screenshots/wines.png)
```

---

## 📦 Installation

```bash
git clone <REPOSITORY_URL>
cd wine_stock

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Running the Application

Development steps:

```bash
source .venv/bin/activate
alembic upgrade head
python main.py
```

End users do **not** need to run migrations.  
The database will be created automatically on first launch.

---

## 🗄️ Database & Migrations

The app uses **SQLite (`wineshop.db`)**.

Developers can apply schema migrations with:

```bash
alembic upgrade head
```

The DB file is created automatically if it does not exist.

---

## 📚 Documentation

Generate and view API documentation locally:

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

Database logic and helper utilities are covered by automated tests.  
UI testing is done manually due to CustomTkinter constraints, and these tests were performed on both WSL (Ubuntu) and Windows 11 environments.

---

## 🖥️ Packaging (Windows Executable)

Build a standalone executable:

```bash
pyinstaller --noconfirm --onefile --windowed main.py
```

This is intended for distribution; the repository contains the reference source code.

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

This project is shared for portfolio and educational purposes only.  
Commercial use or redistribution requires permission.

---

<p align="center">
  Made with ❤️ for learning, building, and improving real-world Python applications.
</p>
