import customtkinter as ctk

import db.events
from decimal import Decimal
from db.models import Session, Shop, Colour, Style, Varietal, Wine
from helpers import populate_db_model, get_by_id
from ui.main_window import MainWindow


def main():
    
    # == DB config ==
    session = Session()    
    # Populate colour and style columns
    wine_colours = ["red", "rosé", "orange", "white", "other"]
    wine_styles = ["dessert", "fortified", "sparkling", "still", "other"]
    wine_varietals = ["baga", "cabernet sauvignon", "grenache", "hondarrabi zuri", 
    "malbec", "moscato bianco", "tinta roriz", "torrontés", "touriga nacional","other"]
    populate_db_model(wine_colours, Colour, session)
    populate_db_model(wine_styles, Style, session)
    populate_db_model(wine_varietals, Varietal, session)

    # Create default shop values if it is first time using the app
    Shop.get_singleton(session)

    # == App config ==
    root = ctk.CTk()
    app_wine_stock = MainWindow(root, session)
    app_wine_stock.root.mainloop()
    
    # == Close db session ==
    session.close()

if __name__ == "__main__":
    main()