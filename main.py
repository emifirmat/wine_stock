"""
Application entry point and initialization.

This module initializes the database, populates default data,
and launches the main application window.
"""
import customtkinter as ctk
from argparse import ArgumentParser, Namespace

from db.bootstrap import ensure_db_ready
from db.sample_data import seed_sample_data
from db.session_factory import build_session
from ui.main_window import MainWindow


def main() -> None:
    """
    Initialise and run the wine stock management application.
    
    Sets up the database with default values, creates the main window,
    and starts the application event loop. Ensures proper cleanup of
    database resources on exit.
    """
    # Ensure database schema is up to date
    ensure_db_ready()
    
    # Parse command-line arguments
    args = parse_args()
    
    # Initialise database session
    session = build_session()    

    # Populate demo data if requested
    if args.demo:
        seed_sample_data(session, with_transactions=args.with_transactions)

    # Initialise and run application
    root = ctk.CTk()
    app_wine_stock = MainWindow(root, session)
    app_wine_stock.root.mainloop()
    
    # Clean up database session
    session.close()

def parse_args() -> Namespace:
    """
    Parse command-line arguments for the application.

    Supports enabling demo mode with optional sample transactions for
    testing and demonstration purposes.
    
    Returns:
        Parsed arguments namespace containing demo and with_transactions flags
    """
    parser = ArgumentParser(description="WineStock Application")

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Load demo wines into the database"
    )
    parser.add_argument(
        "--with-transactions",
        action="store_true",
        help="Include sample transactions when using --demo"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()