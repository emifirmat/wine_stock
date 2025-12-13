"""
Database and resource path bootstrapping utilities.

This module provides utilities for managing database locations, resource paths,
and Alembic migrations across development, production, and PyInstaller environments.
"""
import os
import sys
from pathlib import Path
from alembic import command
from alembic.config import Config


# == Runtime Environment Detection ==
def is_frozen() -> bool:
    """
    Check if running from a PyInstaller-built executable.
    
    Returns:
        True if running as a bundled executable, False in development
    """
    return bool(getattr(sys, "frozen", False))

# == Path Resolution ==
def project_root() -> Path:
    """
    Resolve the project root directory.
    
    Assumes this file lives at <root>/db/bootstrap.py. This works reliably
    in development and serves as a fallback for other environments.
    
    Returns:
        Path to project root directory
    """
    return Path(__file__).resolve().parents[1]


def resource_path(relative: str) -> str:
    """
    Build an absolute path to a bundled resource.
    
    Handles different resource locations depending on runtime environment:
    - PyInstaller --onefile: Resources extracted to sys._MEIPASS
    - Development: Resources resolved relative to project root
    
    Parameters:
        relative: Relative path to resource from project root
        
    Returns:
        Absolute path to the resource as a string
        
    Examples:
        resource_path("alembic.ini") → "/path/to/project/alembic.ini" (dev)
        resource_path("alembic.ini") → "/tmp/_MEI123/alembic.ini" (bundled)
    """
    base = Path(getattr(sys, "_MEIPASS", project_root()))
    return str(base / relative)


def appdata_dir(app_name: str = "WineStock") -> Path:
    """
    et per-user application data directory.
    
    Creates the directory if it doesn't exist. Platform-specific behavior:
    - Windows: Prefers LOCALAPPDATA, falls back to APPDATA, then user home
    - Other platforms: Falls back to user home directory
    
    Parameters:
        app_name: Application name for directory (default: "WineStock")
        
    Returns:
        Path to application data directory
        
    Examples:
        Windows: C:\\Users\\username\\AppData\\Local\\WineStock
        Linux: /home/username/WineStock
    """
    base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
    base_path = Path(base) if base else Path.home()
    path = base_path / app_name
    path.mkdir(parents=True, exist_ok=True)
    return path

# == Database Path Management ==
def dev_db_path(filename: str = "wineshop.db") -> Path:
    """
    Get development database path.
    
    Database stored in project root for easy access during development.
    
    Parameters:
        filename: Database filename (default: "wineshop.db")
        
    Returns:
        Path to development database
    """
    return project_root() / filename


def prod_db_path(filename: str = "wineshop.db") -> Path:
    """
    Get production database path.
    
    Database stored in user's AppData directory for production deployment.
    
    Parameters:
        filename: Database filename (default: "wineshop.db")
        
    Returns:
        Path to production database
    """
    return appdata_dir() / filename


def get_db_path(filename: str = "wineshop.db") -> Path:
    """
    Determine appropriate database path based on runtime environment.
    
    Logic:
    - Bundled executable: Always use AppData (production)
    - Development:
        - Default: Project root (development)
        - WINESTOCK_ENV=prod: AppData (simulate production)
    
    Parameters:
        filename: Database filename (default: "wineshop.db")
        
    Returns:
        Path to database file
        
    Examples:
        >>> # Running bundled executable
        >>> get_db_path()
        WindowsPath('C:/Users/username/AppData/Local/WineStock/wineshop.db')
        
        >>> # Running in development
        >>> get_db_path()
        PosixPath('/path/to/project/wineshop.db')
        
        >>> # Testing production behavior in dev
        >>> os.environ["WINESTOCK_ENV"] = "prod"
        >>> get_db_path()
        WindowsPath('C:/Users/username/AppData/Local/WineStock/wineshop.db')
    """
    if is_frozen():
        return prod_db_path(filename)

    env = os.environ.get("WINESTOCK_ENV", "dev").strip().lower()
    if env == "prod":
        return prod_db_path(filename)

    return dev_db_path(filename)


def get_sqlalchemy_url() -> str:
    """
    Build SQLite SQLAlchemy connection URL for the chosen database location.
    
    Returns:
        SQLAlchemy connection string
        
    Examples:
        'sqlite:///C:/Users/username/AppData/Local/WineStock/wineshop.db'
        'sqlite:////path/to/project/wineshop.db'
    """
    return f"sqlite:///{get_db_path()}"


# == Database Schema Management (Alembic) ==
def ensure_db_ready() -> Path:
    """
    Ensure database schema exists and is up to date.
    
    Runs Alembic migrations to create or upgrade the database schema to the
    latest version. This must be called before any database operations.
    
    Returns:
        Path to the initialized database file
        
    Note:
        This function configures Alembic dynamically to work in both
        development and PyInstaller bundled environments.
    """
    db_path = get_db_path()

    # Configure Alembic for current environment
    cfg = Config(str(resource_path("alembic.ini")))
    cfg.set_main_option("script_location", str(resource_path("migrations")))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    # Run migrations to latest version (alembic upgrade head)
    command.upgrade(cfg, "head")

    return db_path

