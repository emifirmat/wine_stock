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

    #add_wines(session)

    # Create default shop values if it is first time using the app
    Shop.get_singleton(session)

    # == App config ==
    root = ctk.CTk()
    app_wine_stock = MainWindow(root, session)
    app_wine_stock.root.mainloop()
    
    # == Close db session ==
    session.close()

def add_wines(session):
    """
    Add ten wines in the db.
    inputs:
        - session: DB session.
    """
    wine1= Wine(
        name="Catena Zapata Malbec",
        winery="Catena Zapata",
        colour=get_by_id(Colour, 1, session),
        style=get_by_id(Style, 1, session),
        varietal=get_by_id(Varietal, 1, session),
        vintage_year=2019,
        origin="Mendoza, Argentina",
        code= "AR-MALB-001",
        purchase_price=Decimal("20.50"),
        selling_price=Decimal("65.23"),
        picture_path = "assets/user_images/wines/catena_zapata_malbec.png",
        quantity = 2
    )
    
    wine2= Wine(
        name="Don Melchor Cabernet Sauvignon",
        winery="Concha y Toro",
        colour=get_by_id(Colour, 1, session),
        style=get_by_id(Style, 1, session),
        varietal=get_by_id(Varietal, 2, session),
        vintage_year=2020,
        origin="Puente Alto, Chile",
        code= "CL-CABS-001",
        purchase_price=Decimal("30.00"),
        selling_price=Decimal("55.00"),
        picture_path = "assets/user_images/wines/don_melchor_cab_sav.png"
    )
    wine3= Wine(
        name="Norton Reserva Malbec",
        winery="Bodega Norton",
        colour=get_by_id(Colour, 1, session),
        style=get_by_id(Style, 1, session),
        varietal=get_by_id(Varietal, 1, session),
        vintage_year=2021,
        origin="Mendoza, Argentina",
        code= "AR-MALB-002",
        purchase_price=Decimal("12.00"),
        selling_price=Decimal("22.00"),

    )
    wine4=Wine(
        name="Susana Balbo Crios Torrontés",
        winery="Susana Balbo Wines",
        colour=get_by_id(Colour, 2, session),
        style=get_by_id(Style, 1, session),
        varietal=get_by_id(Varietal, 3, session),
        vintage_year=2022,
        origin="Cafayate, Argentina",
        code="AR-TORR-001",
        purchase_price=Decimal("9.50"),
        selling_price=Decimal("17.00"),

    )
    wine5= Wine(
        name="Martini Asti Spumante",
        winery="Martini & Rossi",
        colour=get_by_id(Colour, 2, session),
        style=get_by_id(Style, 2, session),
        varietal=get_by_id(Varietal, 4, session),
        vintage_year=2021,
        origin="Asti, Italy",
        code= "IT-SPAR-001",
        purchase_price=Decimal("9.00"),
        selling_price=Decimal("16.00"),
        picture_path = "assets/user_images/wines/martini_anti_spumante.jpg",
        quantity = 9

    )
    wine6=Wine(
        name="Fonseca Bin 27",
        winery="Fonseca",
        colour=get_by_id(Colour, 1, session),
        style=get_by_id(Style, 3, session),
        varietal=get_by_id(Varietal, 5, session),
        vintage_year=2019,
        origin="Douro, Portugal",
        code= "PT-PORT-001",
        purchase_price=Decimal("14.00"),
        selling_price=Decimal("25.00"),
        picture_path = "assets/user_images/wines/fonseca_bin_27.jpg"
    )
    wine7=Wine(
        name="Mateus Rosé",
        winery="Sogrape Vinhos",
        colour=get_by_id(Colour, 3, session),
        style=get_by_id(Style, 2, session),
        varietal=get_by_id(Varietal, 6, session),
        vintage_year=2022,
        origin="Douro, Portugal",
        code= "PT-ROSE-001",
        purchase_price=Decimal("5.50"),
        selling_price=Decimal("10.00"),
    )
    wine8=Wine(
        name="Château d'Esclans Whispering Angel",
        winery="Château d'Esclans",
        colour=get_by_id(Colour, 3, session),
        style=get_by_id(Style, 1, session),
        varietal=get_by_id(Varietal, 7, session),
        vintage_year=2021,
        origin="Provence, France",
        code= "FR-ROSE-002",
        purchase_price=Decimal("15.00"),
        selling_price=Decimal("27.00"),
        quantity = 11
    )
    wine9=Wine(
        name="Txakoli Ameztoi Rubentis",
        winery="Ameztoi",
        colour=get_by_id(Colour, 5, session),
        style=get_by_id(Style, 5, session),
        varietal=get_by_id(Varietal, 8, session),
        vintage_year=2022,
        origin="Getariako Txakolina, Spain",
        code= "ES-OTH-001",
        purchase_price=Decimal("13.00"),
        selling_price=Decimal("22.00"),
        quantity = 1
    )
    wine10= Wine(
        name="Niepoort Ruby Port",
        winery="Niepoort",
        colour=get_by_id(Colour, 1, session),
        style=get_by_id(Style, 3, session),
        varietal=get_by_id(Varietal, 9, session),
        vintage_year=2020,
        origin="Douro, Portugal",
        code= "PT-PORT-002",
        purchase_price=Decimal("18.00"),
        selling_price=Decimal("30.00"),
        quantity = 0
    )

    session.add_all([wine1, wine2, wine3,wine4, wine5, wine6, wine7, wine8, wine9, wine10])
    session.commit()

if __name__ == "__main__":
    main()