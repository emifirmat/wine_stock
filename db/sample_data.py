"""
Database seeding utilities for sample data.

This module provides functions to populate the database with sample wines
and transactions for testing and demonstration purposes.
"""
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from db.models import Wine, Colour, Style, Varietal, StockMovement


def seed_sample_data(session: Session, with_transactions: bool = False) -> None:
    """
    Seed the database with sample data if empty.
    
    Checks if the database already contains wines. If empty, populates with
    30 sample wines and optionally 70 sample transactions.
    
    Parameters:
        session: SQLAlchemy database session
        with_transactions: If True, also adds sample stock movements after wines
    """
    if not session.query(Wine).all():
        add_wines(session)
        if with_transactions:
            add_transactions(session)
    else:
        print(
            "Demo data was not loaded because existing wines were detected.\n"
            "To run the demo, clear all wines first or use a fresh database."
        )

def add_wines(session: Session) -> None:
    """
    Populate the database with 30 sample wines for testing.
    
    Creates a diverse collection of wines including various colors, styles,
    varietals, and origins. Some wines include custom images, while others
    use defaults. Includes intentionally invalid image paths for testing
    error handling.
    
    Parameters:
        session: SQLAlchemy database session
    """
    # Cache references to Wine's Foreing Keys
    colours = {c.name: c for c in session.query(Colour).all()}
    styles = {s.name: s for s in session.query(Style).all()}
    varietals = {v.name: v for v in session.query(Varietal).all()}

    # Set wine specifications
    wine_specs = [
        {
            "name": "Catena Zapata Malbec",
            "winery": "Catena Zapata",
            "colour": "red",
            "style": "still",
            "varietal": "malbec",
            "vintage_year": 2019,
            "origin": "Mendoza, Argentina",
            "code": "AR-MALB-001",
            "purchase_price": Decimal("20.50"),
            "selling_price": Decimal("65.23"),
            "picture_path": "assets/user_images/wines/catena_zapata_malbec.png",
            "quantity": 2,
        },
        {
            "name": "Don Melchor Cabernet Sauvignon",
            "winery": "Concha y Toro",
            "colour": "red",
            "style": "still",
            "varietal": "cabernet sauvignon",
            "vintage_year": 2020,
            "origin": "Puente Alto, Chile",
            "code": "CL-CABS-001",
            "purchase_price": Decimal("30.00"),
            "selling_price": Decimal("55.00"),
            "picture_path": "assets/user_images/wines/don_melchor_cab_sav.png",
        },
        {
            "name": "Norton Reserva Malbec",
            "winery": "Bodega Norton",
            "colour": "red",
            "style": "still",
            "varietal": "malbec",
            "vintage_year": 2021,
            "origin": "Mendoza, Argentina",
            "code": "AR-MALB-002",
            "purchase_price": Decimal("12.00"),
            "selling_price": Decimal("22.00"),
        },
        {
            "name": "Susana Balbo Crios Torrontés",
            "winery": "Susana Balbo Wines",
            "colour": "white",
            "style": "still",
            "varietal": "torrontés",
            "vintage_year": 2022,
            "origin": "Cafayate, Argentina",
            "code": "AR-TORR-001",
            "purchase_price": Decimal("9.50"),
            "selling_price": Decimal("17.00"),
        },
        {
            "name": "Martini Asti Spumante",
            "winery": "Martini & Rossi",
            "colour": "white",
            "style": "sparkling",
            "varietal": "moscato bianco",
            "vintage_year": 2021,
            "origin": "Asti, Italy",
            "code": "IT-SPAR-001",
            "purchase_price": Decimal("9.00"),
            "selling_price": Decimal("16.00"),
            "picture_path": "assets/user_images/wines/martini_anti_spumante.jpg",
            "quantity": 9,
        },
        {
            "name": "Fonseca Bin 27",
            "winery": "Fonseca",
            "colour": "red",
            "style": "fortified",
            "varietal": "touriga nacional",
            "vintage_year": 2019,
            "origin": "Douro, Portugal",
            "code": "PT-PORT-001",
            "purchase_price": Decimal("14.00"),
            "selling_price": Decimal("25.00"),
            "picture_path": "assets/user_images/wines/fonseca_bin_27.jpg",
        },
        {
            "name": "Mateus Rosé",
            "winery": "Sogrape Vinhos",
            "colour": "rosé",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2022,
            "origin": "Douro, Portugal",
            "code": "PT-ROSE-001",
            "purchase_price": Decimal("5.50"),
            "selling_price": Decimal("10.00"),
        },
        {
            "name": "Château d'Esclans Whispering Angel",
            "winery": "Château d'Esclans",
            "colour": "rosé",
            "style": "still",
            "varietal": "grenache",
            "vintage_year": 2021,
            "origin": "Provence, France",
            "code": "FR-ROSE-002",
            "purchase_price": Decimal("15.00"),
            "selling_price": Decimal("27.00"),
            "quantity": 11,
        },
        {
            "name": "Txakoli Ameztoi Rubentis",
            "winery": "Ameztoi",
            "colour": "rosé",
            "style": "sparkling",
            "varietal": "hondarrabi zuri",
            "vintage_year": 2022,
            "origin": "Getariako Txakolina, Spain",
            "code": "ES-OTH-001",
            "purchase_price": Decimal("13.00"),
            "selling_price": Decimal("22.00"),
            "quantity": 1,
        },
        {
            "name": "Niepoort Ruby Port",
            "winery": "Niepoort",
            "colour": "red",
            "style": "fortified",
            "varietal": "tinta roriz",
            "vintage_year": 2020,
            "origin": "Douro, Portugal",
            "code": "PT-PORT-002",
            "purchase_price": Decimal("18.00"),
            "selling_price": Decimal("30.00"),
            "quantity": 0,
        },
        {
            "name": "Marques de Riscal Reserva",
            "winery": "Marques de Riscal",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2018,
            "origin": "Rioja, Spain",
            "code": "ES-RED-002",
            "purchase_price": Decimal("18.00"),
            "selling_price": Decimal("32.00"),
            "quantity": 10,
            "min_stock": 0,
            "picture_path": None,
        },
        {
            "name": "Penfolds Bin 389",
            "winery": "Penfolds",
            "colour": "red",
            "style": "still",
            "varietal": "cabernet sauvignon",
            "vintage_year": 2019,
            "origin": "South Australia, Australia",
            "code": "AU-RED-001",
            "purchase_price": Decimal("28.00"),
            "selling_price": Decimal("55.00"),
            "quantity": 5,
            "min_stock": 2,
            "picture_path": None,
        },
        {
            "name": "Cloudy Bay Sauvignon Blanc",
            "winery": "Cloudy Bay",
            "colour": "white",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2022,
            "origin": "Marlborough, New Zealand",
            "code": "NZ-WHITE-001",
            "purchase_price": Decimal("20.00"),
            "selling_price": Decimal("35.00"),
            "quantity": 8,
            "min_stock": 3,
            "picture_path": None,
        },
        {
            "name": "Santa Rita 120 Cabernet Sauvignon",
            "winery": "Santa Rita",
            "colour": "red",
            "style": "still",
            "varietal": "cabernet sauvignon",
            "vintage_year": 2021,
            "origin": "Central Valley, Chile",
            "code": "CL-RED-002",
            "purchase_price": Decimal("7.00"),
            "selling_price": Decimal("13.00"),
            "quantity": 12,
            "min_stock": 6,
            "picture_path": None,
        },
        {
            "name": "Trapiche Oak Cask Malbec",
            "winery": "Trapiche",
            "colour": "red",
            "style": "still",
            "varietal": "malbec",
            "vintage_year": 2020,
            "origin": "Mendoza, Argentina",
            "code": "AR-MALB-003",
            "purchase_price": Decimal("9.00"),
            "selling_price": Decimal("18.00"),
            "quantity": 20,
            "min_stock": 5,
            "picture_path": None,
        },
        {
            "name": "Alamos Chardonnay",
            "winery": "Alamos",
            "colour": "white",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2021,
            "origin": "Mendoza, Argentina",
            "code": "AR-WHITE-001",
            "purchase_price": Decimal("8.50"),
            "selling_price": Decimal("15.00"),
            "quantity": 30,
            "min_stock": 10,
            "picture_path": None,
        },
        {
            "name": "Casillero del Diablo Carmenere",
            "winery": "Concha y Toro",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2020,
            "origin": "Central Valley, Chile",
            "code": "CL-RED-003",
            "purchase_price": Decimal("9.00"),
            "selling_price": Decimal("17.00"),
            "quantity": 45,
            "min_stock": 15,
            "picture_path": None,
        },
        {
            "name": "Gallo Family White Zinfandel",
            "winery": "Gallo Family Vineyards",
            "colour": "rosé",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2022,
            "origin": "California, United States",
            "code": "US-ROSE-001",
            "purchase_price": Decimal("6.00"),
            "selling_price": Decimal("11.00"),
            "quantity": 7,
            "min_stock": 4,
            "picture_path": None,
        },
        {
            "name": "Barefoot Merlot",
            "winery": "Barefoot Cellars",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2021,
            "origin": "California, United States",
            "code": "US-RED-001",
            "purchase_price": Decimal("5.00"),
            "selling_price": Decimal("9.50"),
            "quantity": 18,
            "min_stock": 9,
            "picture_path": "wrong_path_for_testing_1.png",
        },
        {
            "name": "Yellow Tail Shiraz",
            "winery": "Casella Wines",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2020,
            "origin": "South Eastern Australia, Australia",
            "code": "AU-RED-002",
            "purchase_price": Decimal("7.00"),
            "selling_price": Decimal("13.00"),
            "quantity": 25,
            "min_stock": 12,
            "picture_path": None,
        },
        {
            "name": "Jacobs Creek Classic Riesling",
            "winery": "Jacobs Creek",
            "colour": "white",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2021,
            "origin": "South Australia, Australia",
            "code": "AU-WHITE-001",
            "purchase_price": Decimal("9.00"),
            "selling_price": Decimal("16.00"),
            "quantity": 40,
            "min_stock": 20,
            "picture_path": None,
        },
        {
            "name": "Kendall Jackson Vintners Reserve Chardonnay",
            "winery": "Kendall Jackson",
            "colour": "white",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2020,
            "origin": "California, United States",
            "code": "US-WHITE-001",
            "purchase_price": Decimal("14.00"),
            "selling_price": Decimal("24.00"),
            "quantity": 3,
            "min_stock": 1,
            "picture_path": None,
        },
        {
            "name": "Villa Maria Private Bin Pinot Gris",
            "winery": "Villa Maria",
            "colour": "white",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2022,
            "origin": "Marlborough, New Zealand",
            "code": "NZ-WHITE-002",
            "purchase_price": Decimal("12.00"),
            "selling_price": Decimal("21.00"),
            "quantity": 16,
            "min_stock": 8,
            "picture_path": None,
        },
        {
            "name": "Tio Pepe Fino Sherry",
            "winery": "Gonzalez Byass",
            "colour": "white",
            "style": "fortified",
            "varietal": "other",
            "vintage_year": 2019,
            "origin": "Jerez, Spain",
            "code": "ES-FORT-001",
            "purchase_price": Decimal("11.00"),
            "selling_price": Decimal("20.00"),
            "quantity": 22,
            "min_stock": 22,
            "picture_path": None,
        },
        {
            "name": "Antinori Tignanello",
            "winery": "Antinori",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2018,
            "origin": "Tuscany, Italy",
            "code": "IT-RED-002",
            "purchase_price": Decimal("65.00"),
            "selling_price": Decimal("120.00"),
            "quantity": 48,
            "min_stock": 48,
            "picture_path": None,
        },
        {
            "name": "Beringer Founders Estate Zinfandel",
            "winery": "Beringer",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2020,
            "origin": "California, United States",
            "code": "US-RED-002",
            "purchase_price": Decimal("10.00"),
            "selling_price": Decimal("18.00"),
            "quantity": 60,
            "min_stock": 80,
            "picture_path": None,
        },
        {
            "name": "Graham Six Grapes Reserve Port",
            "winery": "Graham",
            "colour": "red",
            "style": "fortified",
            "varietal": "touriga nacional",
            "vintage_year": 2019,
            "origin": "Douro, Portugal",
            "code": "PT-PORT-003",
            "purchase_price": Decimal("15.00"),
            "selling_price": Decimal("27.00"),
            "quantity": 75,
            "min_stock": 90,
            "picture_path": "wrong_path_for_testing_2.png",
        },
        {
            "name": "Mumm Cordon Rouge Brut",
            "winery": "G H Mumm",
            "colour": "white",
            "style": "sparkling",
            "varietal": "other",
            "vintage_year": 2020,
            "origin": "Champagne, France",
            "code": "FR-SPARK-001",
            "purchase_price": Decimal("32.00"),
            "selling_price": Decimal("55.00"),
            "quantity": 90,
            "min_stock": 100,
            "picture_path": None,
        },
        {
            "name": "Moet Imperial Brut",
            "winery": "Moet and Chandon",
            "colour": "white",
            "style": "sparkling",
            "varietal": "other",
            "vintage_year": 2019,
            "origin": "Champagne, France",
            "code": "FR-SPARK-002",
            "purchase_price": Decimal("38.00"),
            "selling_price": Decimal("65.00"),
            "quantity": 120,
            "min_stock": 130,
            "picture_path": None,
        },
        {
            "name": "Louis Jadot Beaujolais Villages",
            "winery": "Louis Jadot",
            "colour": "red",
            "style": "still",
            "varietal": "other",
            "vintage_year": 2021,
            "origin": "Beaujolais, France",
            "code": "FR-RED-003",
            "purchase_price": Decimal("13.00"),
            "selling_price": Decimal("22.00"),
            "quantity": 150,
            "min_stock": 160,
            "picture_path": None,
        },
    ]
    
    # Create the wines
    wines = []

    for spec in wine_specs:
        # Work with a copy of the data
        spec = spec.copy()

        spec["colour"] = colours[spec["colour"]]
        spec["style"] = styles[spec["style"]]
        spec["varietal"] = varietals[spec["varietal"]]

        wines.append(Wine(**spec))

    session.add_all(wines)
    session.commit()
    print(f"Succesfully added wine samples ({len(wines)})")

   
def add_transactions(session: Session) -> None:
    """
    Populate the database with 70 sample stock movements for testing.
    
    Creates a comprehensive set of purchase and sale transactions across
    20 different wines. Each wine code is grouped with its transactions
    in comments for easy reference and debugging.
    
    Parameters:
        session: SQLAlchemy database session
    
    Note:
        Transaction quantities are designed to test various scenarios including
        low stock conditions, stock depletion, and high-volume movements.
    """
    # Cache references to StockMovement's Foreing Key
    wines = {w.code: w for w in session.query(Wine).all()}
    
    # Transaction specs
    transaction_specs = [
        # AR-MALB-001
        ("AR-MALB-001", datetime(2023, 11, 5, 10, 0, 0), "purchase", 5, Decimal("20.50")),
        ("AR-MALB-001", datetime(2023, 12, 5, 10, 0, 0), "sale",     2, Decimal("65.23")),
        ("AR-MALB-001", datetime(2024,  1, 5, 10, 0, 0), "sale",     2, Decimal("65.23")),
        ("AR-MALB-001", datetime(2024,  2, 5, 10, 0, 0), "sale",     3, Decimal("65.23")),
        ("AR-MALB-001", datetime(2024,  3, 5, 10, 0, 0), "sale",     3, Decimal("65.23")),

        # AR-MALB-003
        ("AR-MALB-003", datetime(2024,  4, 5, 10, 0, 0), "purchase", 14, Decimal("9.00")),
        ("AR-MALB-003", datetime(2024,  5, 5, 10, 0, 0), "sale",     10, Decimal("18.00")),
        ("AR-MALB-003", datetime(2024,  6, 5, 10, 0, 0), "sale",     16, Decimal("18.00")),

        # AR-TORR-001
        ("AR-TORR-001", datetime(2024,  7, 5, 10, 0, 0), "purchase", 10, Decimal("9.50")),
        ("AR-TORR-001", datetime(2024,  8, 5, 10, 0, 0), "purchase", 11, Decimal("9.50")),
        ("AR-TORR-001", datetime(2024,  9, 5, 10, 0, 0), "sale",      9, Decimal("17.00")),
        ("AR-TORR-001", datetime(2024, 10, 5, 10, 0, 0), "sale",     11, Decimal("17.00")),

        # AR-WHITE-001
        ("AR-WHITE-001", datetime(2024, 11, 5, 10, 0, 0), "sale",      8, Decimal("15.00")),
        ("AR-WHITE-001", datetime(2024, 12, 5, 10, 0, 0), "sale",      9, Decimal("15.00")),

        # AU-RED-001
        ("AU-RED-001", datetime(2025,  1, 5, 10, 0, 0), "purchase", 19, Decimal("28.00")),
        ("AU-RED-001", datetime(2025,  2, 5, 10, 0, 0), "sale",      7, Decimal("55.00")),
        ("AU-RED-001", datetime(2025,  3, 5, 10, 0, 0), "sale",      8, Decimal("55.00")),

        # AU-RED-002
        ("AU-RED-002", datetime(2025,  4, 5, 10, 0, 0), "purchase", 11, Decimal("7.00")),
        ("AU-RED-002", datetime(2025,  5, 5, 10, 0, 0), "sale",     15, Decimal("13.00")),
        ("AU-RED-002", datetime(2025,  6, 5, 10, 0, 0), "sale",     19, Decimal("13.00")),

        # AU-WHITE-001
        ("AU-WHITE-001", datetime(2025,  7, 5, 10, 0, 0), "purchase",  5, Decimal("9.00")),
        ("AU-WHITE-001", datetime(2025,  8, 5, 10, 0, 0), "sale",     20, Decimal("16.00")),
        ("AU-WHITE-001", datetime(2025,  9, 5, 10, 0, 0), "sale",     18, Decimal("16.00")),

        # CL-CABS-001
        ("CL-CABS-001", datetime(2025, 10, 5, 10, 0, 0), "purchase",  6, Decimal("30.00")),
        ("CL-CABS-001", datetime(2025, 11, 5, 10, 0, 0), "sale",      2, Decimal("55.00")),
        ("CL-CABS-001", datetime(2025, 12, 5, 10, 0, 0), "sale",      2, Decimal("55.00")),
        ("CL-CABS-001", datetime(2025, 12,10, 10, 0, 0), "sale",      2, Decimal("55.00")),

        # CL-RED-002
        ("CL-RED-002",  datetime(2025, 12,10, 10, 0, 0), "purchase",  5, Decimal("7.00")),
        ("CL-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      7, Decimal("13.00")),
        ("CL-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      7, Decimal("13.00")),

        # CL-RED-003
        ("CL-RED-003",  datetime(2025, 12,10, 10, 0, 0), "purchase",  8, Decimal("9.00")),
        ("CL-RED-003",  datetime(2025, 12,10, 10, 0, 0), "sale",     13, Decimal("17.00")),
        ("CL-RED-003",  datetime(2025, 12,10, 10, 0, 0), "sale",     15, Decimal("17.00")),

        # ES-FORT-001
        ("ES-FORT-001", datetime(2025, 12,10, 10, 0, 0), "purchase", 14, Decimal("11.00")),
        ("ES-FORT-001", datetime(2025, 12,10, 10, 0, 0), "sale",     13, Decimal("20.00")),
        ("ES-FORT-001", datetime(2025, 12,10, 10, 0, 0), "sale",     13, Decimal("20.00")),

        # ES-RED-002
        ("ES-RED-002",  datetime(2025, 12,10, 10, 0, 0), "purchase", 11, Decimal("18.00")),
        ("ES-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      5, Decimal("32.00")),
        ("ES-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      7, Decimal("32.00")),

        # FR-RED-003 (incluye la única cantidad de 3 dígitos)
        ("FR-RED-003",  datetime(2025, 12,10, 10, 0, 0), "purchase",120, Decimal("65.00")),
        ("FR-RED-003",  datetime(2025, 12,10, 10, 0, 0), "purchase", 11, Decimal("65.00")),
        ("FR-RED-003",  datetime(2025, 12,10, 10, 0, 0), "sale",      4, Decimal("22.00")),
        ("FR-RED-003",  datetime(2025, 12,10, 10, 0, 0), "sale",      6, Decimal("22.00")),

        # FR-ROSE-002
        ("FR-ROSE-002", datetime(2025, 12,10, 10, 0, 0), "purchase", 17, Decimal("15.00")),
        ("FR-ROSE-002", datetime(2025, 12,10, 10, 0, 0), "sale",      7, Decimal("27.00")),
        ("FR-ROSE-002", datetime(2025, 12,10, 10, 0, 0), "sale",      9, Decimal("27.00")),

        # IT-RED-002
        ("IT-RED-002",  datetime(2025, 12,10, 10, 0, 0), "purchase",  8, Decimal("65.00")),
        ("IT-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      2, Decimal("120.00")),
        ("IT-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      2, Decimal("120.00")),

        # IT-SPAR-001
        ("IT-SPAR-001", datetime(2025, 12,10, 10, 0, 0), "purchase",  8, Decimal("9.00")),
        ("IT-SPAR-001", datetime(2025, 12,10, 10, 0, 0), "sale",      8, Decimal("16.00")),
        ("IT-SPAR-001", datetime(2025, 12,10, 10, 0, 0), "sale",      9, Decimal("16.00")),

        # NZ-WHITE-002
        ("NZ-WHITE-002",datetime(2025, 12,10, 10, 0, 0), "sale",      3, Decimal("21.00")),
        ("NZ-WHITE-002",datetime(2025, 12,10, 10, 0, 0), "sale",      4, Decimal("21.00")),
        ("NZ-WHITE-002",datetime(2025, 12,10, 10, 0, 0), "sale",      4, Decimal("21.00")),

        # PT-PORT-001
        ("PT-PORT-001", datetime(2025, 12,10, 10, 0, 0), "purchase",  9, Decimal("14.00")),
        ("PT-PORT-001", datetime(2025, 12,10, 10, 0, 0), "sale",      4, Decimal("25.00")),
        ("PT-PORT-001", datetime(2025, 12,10, 10, 0, 0), "sale",      5, Decimal("25.00")),

        # PT-PORT-003
        ("PT-PORT-003", datetime(2025, 12,10, 10, 0, 0), "purchase", 17, Decimal("15.00")),
        ("PT-PORT-003", datetime(2025, 12,10, 10, 0, 0), "sale",      3, Decimal("27.00")),
        ("PT-PORT-003", datetime(2025, 12,10, 10, 0, 0), "sale",      3, Decimal("27.00")),

        # US-RED-001
        ("US-RED-001",  datetime(2025, 12,10, 10, 0, 0), "purchase", 10, Decimal("5.00")),
        ("US-RED-001",  datetime(2025, 12,10, 10, 0, 0), "sale",      8, Decimal("9.50")),
        ("US-RED-001",  datetime(2025, 12,10, 10, 0, 0), "sale",      8, Decimal("9.50")),

        # US-RED-002
        ("US-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      8, Decimal("18.00")),
        ("US-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      9, Decimal("18.00")),
        ("US-RED-002",  datetime(2025, 12,10, 10, 0, 0), "sale",      9, Decimal("18.00")),

        # US-ROSE-001
        ("US-ROSE-001", datetime(2025, 12,10, 10, 0, 0), "purchase", 17, Decimal("6.00")),
        ("US-ROSE-001", datetime(2025, 12,10, 10, 0, 0), "sale",      9, Decimal("11.00")),
        ("US-ROSE-001", datetime(2025, 12,10, 10, 0, 0), "sale",      9, Decimal("11.00")),
    ]

    # Create stock movements
    movements = []
    for code, dt, transaction_type, quantity, price in transaction_specs:
        movements.append(
            StockMovement(
                wine=wines[code],
                datetime=dt,
                transaction_type=transaction_type,
                quantity=quantity,
                price=price
            )
        )

    session.add_all(movements)
    session.commit()

    print(f"Successfully added transaction samples ({len(movements)})")
