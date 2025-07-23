import customtkinter as ctk

from models import Session, Shop, Wine, Colour, Style, Varietal
from helpers import populate_db_model

from ui.main_window import MainWindow

def main():
    
    # DB config
    session = Session()    
    # Populate colour and style columns
    wine_colours = ["red", "white", "rosé", "orange", "other"]
    wine_styles = ["still", "sparkling", "fortified", "dessert", "other"]
    populate_db_model(wine_colours, Colour, session)
    populate_db_model(wine_styles, Style, session)

    # App config
    root = ctk.CTk()
    app_wine_stock = MainWindow(root)
    app_wine_stock.root.mainloop()


if __name__ == "__main__":
    main()