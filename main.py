from .models import Session, Shop, Wine, Colour, Style, Varietal
from .helpers import populate_db_model

def main():
    session = Session()
    
    # SPopulate colour and style columns
    wine_colours = ["red", "white", "rosé", "orange", "other"]
    wine_styles = ["still", "sparkling", "fortified", "dessert", "other"]
    populate_db_model(wine_colours, Colour, session)
    populate_db_model(wine_styles, Style, session)

    


if __name__ == "__main__":
    main()