import customtkinter as ctk

from models import Session, Shop, Wine, Colour, Style, Varietal
from helpers import populate_db_model

from ui.main_window import MainWindow

def main():
    
    # == DB config ==
    session = Session()    
    # Populate colour and style columns
    wine_colours = ["red", "white", "rosé", "orange", "other"]
    wine_styles = ["still", "sparkling", "fortified", "dessert", "other"]
    populate_db_model(wine_colours, Colour, session)
    populate_db_model(wine_styles, Style, session)
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