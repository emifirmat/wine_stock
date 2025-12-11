"""
Application entry point and initialization.

This module initializes the database, populates default data,
and launches the main application window.
"""
import customtkinter as ctk
from argparse import ArgumentParser, Namespace

import db.events # Don't remove this
from db.sample_data import seed_sample_data
from db.models import Session, Shop, Colour, Style, Varietal
from helpers import populate_db_model
from ui.main_window import MainWindow


def main() -> None:
    """
    Initialize and run the wine stock management application.
    
    Sets up the database with default values, creates the main window,
    and starts the application event loop.
    """
    args = parse_args()
    
    # == DB config ==
    session = Session()    
    
    # Populate colour, style, and varietal tables with default values
    wine_colours = ["red", "rosé", "orange", "white", "other"]
    wine_styles = ["dessert", "fortified", "sparkling", "still", "other"]
    wine_varietals = ["baga", "cabernet sauvignon", "grenache", "hondarrabi zuri", 
    "malbec", "moscato bianco", "tinta roriz", "torrontés", "touriga nacional","other"]
    populate_db_model(wine_colours, Colour, session)
    populate_db_model(wine_styles, Style, session)
    populate_db_model(wine_varietals, Varietal, session)

    # Create default shop values if it is first time using the app
    Shop.get_singleton(session)

    # == Demo ==
    if args.demo:
        seed_sample_data(session, with_transactions=args.with_transactions)

    # == App config ==
    root = ctk.CTk()
    app_wine_stock = MainWindow(root, session)
    app_wine_stock.root.mainloop()
    
    # == Close db session ==
    session.close()

def parse_args() -> Namespace:
    """
    Parse command-line arguments for the application.

    Supports enabling demo mode and optionally including
    sample transactions when seeding data.
    
    Returns:
        Parsed arguments namespace.
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