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
    wine1 = Wine(
        name="Catena Zapata Malbec",
        winery="Catena Zapata",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="malbec"),
        vintage_year=2019,
        origin="Mendoza, Argentina",
        code="AR-MALB-001",
        purchase_price=Decimal("20.50"),
        selling_price=Decimal("65.23"),
        picture_path="assets/user_images/wines/catena_zapata_malbec.png",
        quantity=2
    )

    wine2 = Wine(
        name="Don Melchor Cabernet Sauvignon",
        winery="Concha y Toro",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="cabernet sauvignon"),
        vintage_year=2020,
        origin="Puente Alto, Chile",
        code="CL-CABS-001",
        purchase_price=Decimal("30.00"),
        selling_price=Decimal("55.00"),
        picture_path="assets/user_images/wines/don_melchor_cab_sav.png"
    )

    wine3 = Wine(
        name="Norton Reserva Malbec",
        winery="Bodega Norton",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="malbec"),
        vintage_year=2021,
        origin="Mendoza, Argentina",
        code="AR-MALB-002",
        purchase_price=Decimal("12.00"),
        selling_price=Decimal("22.00"),
    )

    wine4 = Wine(
        name="Susana Balbo Crios Torrontés",
        winery="Susana Balbo Wines",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="torrontés"),
        vintage_year=2022,
        origin="Cafayate, Argentina",
        code="AR-TORR-001",
        purchase_price=Decimal("9.50"),
        selling_price=Decimal("17.00"),
    )

    wine5 = Wine(
        name="Martini Asti Spumante",
        winery="Martini & Rossi",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="sparkling"),
        varietal=Varietal.get_by_filter(session, name="moscato bianco"),
        vintage_year=2021,
        origin="Asti, Italy",
        code="IT-SPAR-001",
        purchase_price=Decimal("9.00"),
        selling_price=Decimal("16.00"),
        picture_path="assets/user_images/wines/martini_anti_spumante.jpg",
        quantity=9
    )

    wine6 = Wine(
        name="Fonseca Bin 27",
        winery="Fonseca",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="fortified"),
        varietal=Varietal.get_by_filter(session, name="touriga nacional"),
        vintage_year=2019,
        origin="Douro, Portugal",
        code="PT-PORT-001",
        purchase_price=Decimal("14.00"),
        selling_price=Decimal("25.00"),
        picture_path="assets/user_images/wines/fonseca_bin_27.jpg"
    )

    wine7 = Wine(
        name="Mateus Rosé",
        winery="Sogrape Vinhos",
        colour=Colour.get_by_filter(session, name="rosé"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2022,
        origin="Douro, Portugal",
        code="PT-ROSE-001",
        purchase_price=Decimal("5.50"),
        selling_price=Decimal("10.00"),
    )

    wine8 = Wine(
        name="Château d'Esclans Whispering Angel",
        winery="Château d'Esclans",
        colour=Colour.get_by_filter(session, name="rosé"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="grenache"),
        vintage_year=2021,
        origin="Provence, France",
        code="FR-ROSE-002",
        purchase_price=Decimal("15.00"),
        selling_price=Decimal("27.00"),
        quantity=11
    )

    wine9 = Wine(
        name="Txakoli Ameztoi Rubentis",
        winery="Ameztoi",
        colour=Colour.get_by_filter(session, name="rosé"),
        style=Style.get_by_filter(session, name="sparkling"),
        varietal=Varietal.get_by_filter(session, name="hondarrabi zuri"),
        vintage_year=2022,
        origin="Getariako Txakolina, Spain",
        code="ES-OTH-001",
        purchase_price=Decimal("13.00"),
        selling_price=Decimal("22.00"),
        quantity=1
    )

    wine10 = Wine(
        name="Niepoort Ruby Port",
        winery="Niepoort",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="fortified"),
        varietal=Varietal.get_by_filter(session, name="tinta roriz"),
        vintage_year=2020,
        origin="Douro, Portugal",
        code="PT-PORT-002",
        purchase_price=Decimal("18.00"),
        selling_price=Decimal("30.00"),
        quantity=0
    )

    wine11 = Wine(
        name="Marques de Riscal Reserva",
        winery="Marques de Riscal",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2018,
        origin="Rioja, Spain",
        code="ES-RED-002",
        purchase_price=Decimal("18.00"),
        selling_price=Decimal("32.00"),
        quantity=10,
        min_stock=0,
        picture_path=None
    )

    wine12 = Wine(
        name="Penfolds Bin 389",
        winery="Penfolds",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="cabernet sauvignon"),
        vintage_year=2019,
        origin="South Australia, Australia",
        code="AU-RED-001",
        purchase_price=Decimal("28.00"),
        selling_price=Decimal("55.00"),
        quantity=5,
        min_stock=2,
        picture_path=None
    )

    wine13 = Wine(
        name="Cloudy Bay Sauvignon Blanc",
        winery="Cloudy Bay",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2022,
        origin="Marlborough, New Zealand",
        code="NZ-WHITE-001",
        purchase_price=Decimal("20.00"),
        selling_price=Decimal("35.00"),
        quantity=8,
        min_stock=3,
        picture_path=None
    )

    wine14 = Wine(
        name="Santa Rita 120 Cabernet Sauvignon",
        winery="Santa Rita",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="cabernet sauvignon"),
        vintage_year=2021,
        origin="Central Valley, Chile",
        code="CL-RED-002",
        purchase_price=Decimal("7.00"),
        selling_price=Decimal("13.00"),
        quantity=12,
        min_stock=6,
        picture_path=None
    )

    wine15 = Wine(
        name="Trapiche Oak Cask Malbec",
        winery="Trapiche",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="malbec"),
        vintage_year=2020,
        origin="Mendoza, Argentina",
        code="AR-MALB-003",
        purchase_price=Decimal("9.00"),
        selling_price=Decimal("18.00"),
        quantity=20,
        min_stock=5,
        picture_path=None
    )

    wine16 = Wine(
        name="Alamos Chardonnay",
        winery="Alamos",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2021,
        origin="Mendoza, Argentina",
        code="AR-WHITE-001",
        purchase_price=Decimal("8.50"),
        selling_price=Decimal("15.00"),
        quantity=30,
        min_stock=10,
        picture_path=None
    )

    wine17 = Wine(
        name="Casillero del Diablo Carmenere",
        winery="Concha y Toro",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2020,
        origin="Central Valley, Chile",
        code="CL-RED-003",
        purchase_price=Decimal("9.00"),
        selling_price=Decimal("17.00"),
        quantity=45,
        min_stock=15,
        picture_path=None
    )

    wine18 = Wine(
        name="Gallo Family White Zinfandel",
        winery="Gallo Family Vineyards",
        colour=Colour.get_by_filter(session, name="rosé"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2022,
        origin="California, United States",
        code="US-ROSE-001",
        purchase_price=Decimal("6.00"),
        selling_price=Decimal("11.00"),
        quantity=7,
        min_stock=4,
        picture_path=None
    )

    wine19 = Wine(
        name="Barefoot Merlot",
        winery="Barefoot Cellars",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2021,
        origin="California, United States",
        code="US-RED-001",
        purchase_price=Decimal("5.00"),
        selling_price=Decimal("9.50"),
        quantity=18,
        min_stock=9,
        picture_path="wrong_path_for_testing_1.png"
    )

    wine20 = Wine(
        name="Yellow Tail Shiraz",
        winery="Casella Wines",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2020,
        origin="South Eastern Australia, Australia",
        code="AU-RED-002",
        purchase_price=Decimal("7.00"),
        selling_price=Decimal("13.00"),
        quantity=25,
        min_stock=12,
        picture_path=None
    )

    wine21 = Wine(
        name="Jacobs Creek Classic Riesling",
        winery="Jacobs Creek",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2021,
        origin="South Australia, Australia",
        code="AU-WHITE-001",
        purchase_price=Decimal("9.00"),
        selling_price=Decimal("16.00"),
        quantity=40,
        min_stock=20,
        picture_path=None
    )

    wine22 = Wine(
        name="Kendall Jackson Vintners Reserve Chardonnay",
        winery="Kendall Jackson",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2020,
        origin="California, United States",
        code="US-WHITE-001",
        purchase_price=Decimal("14.00"),
        selling_price=Decimal("24.00"),
        quantity=3,
        min_stock=1,
        picture_path=None
    )

    wine23 = Wine(
        name="Villa Maria Private Bin Pinot Gris",
        winery="Villa Maria",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2022,
        origin="Marlborough, New Zealand",
        code="NZ-WHITE-002",
        purchase_price=Decimal("12.00"),
        selling_price=Decimal("21.00"),
        quantity=16,
        min_stock=8,
        picture_path=None
    )

    wine24 = Wine(
        name="Tio Pepe Fino Sherry",
        winery="Gonzalez Byass",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="fortified"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2019,
        origin="Jerez, Spain",
        code="ES-FORT-001",
        purchase_price=Decimal("11.00"),
        selling_price=Decimal("20.00"),
        quantity=22,
        min_stock=22,
        picture_path=None
    )

    wine25 = Wine(
        name="Antinori Tignanello",
        winery="Antinori",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2018,
        origin="Tuscany, Italy",
        code="IT-RED-002",
        purchase_price=Decimal("65.00"),
        selling_price=Decimal("120.00"),
        quantity=48,
        min_stock=48,
        picture_path=None
    )

    wine26 = Wine(
        name="Beringer Founders Estate Zinfandel",
        winery="Beringer",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2020,
        origin="California, United States",
        code="US-RED-002",
        purchase_price=Decimal("10.00"),
        selling_price=Decimal("18.00"),
        quantity=60,
        min_stock=80,
        picture_path=None
    )

    wine27 = Wine(
        name="Graham Six Grapes Reserve Port",
        winery="Graham",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="fortified"),
        varietal=Varietal.get_by_filter(session, name="touriga nacional"),
        vintage_year=2019,
        origin="Douro, Portugal",
        code="PT-PORT-003",
        purchase_price=Decimal("15.00"),
        selling_price=Decimal("27.00"),
        quantity=75,
        min_stock=90,
        picture_path="wrong_path_for_testing_2.png"
    )

    wine28 = Wine(
        name="Mumm Cordon Rouge Brut",
        winery="G H Mumm",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="sparkling"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2020,
        origin="Champagne, France",
        code="FR-SPARK-001",
        purchase_price=Decimal("32.00"),
        selling_price=Decimal("55.00"),
        quantity=90,
        min_stock=100,
        picture_path=None
    )

    wine29 = Wine(
        name="Moet Imperial Brut",
        winery="Moet and Chandon",
        colour=Colour.get_by_filter(session, name="white"),
        style=Style.get_by_filter(session, name="sparkling"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2019,
        origin="Champagne, France",
        code="FR-SPARK-002",
        purchase_price=Decimal("38.00"),
        selling_price=Decimal("65.00"),
        quantity=120,
        min_stock=130,
        picture_path=None
    )

    wine30 = Wine(
        name="Louis Jadot Beaujolais Villages",
        winery="Louis Jadot",
        colour=Colour.get_by_filter(session, name="red"),
        style=Style.get_by_filter(session, name="still"),
        varietal=Varietal.get_by_filter(session, name="other"),
        vintage_year=2021,
        origin="Beaujolais, France",
        code="FR-RED-003",
        purchase_price=Decimal("13.00"),
        selling_price=Decimal("22.00"),
        quantity=150,
        min_stock=160,
        picture_path=None
    )


    session.add_all([
        wine1, wine2, wine3, wine4, wine5,
        wine6, wine7, wine8, wine9, wine10,
        wine11, wine12, wine13, wine14, wine15,
        wine16, wine17, wine18, wine19, wine20,
        wine21, wine22, wine23, wine24, wine25,
        wine26, wine27, wine28, wine29, wine30,
    ])
    session.commit()

   
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
    # AR-MALB-001: 1 purchase (5) + 4 sales (2,2,3,3) = -3
    t1 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-001"),
        datetime=datetime(2023, 11, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=5,
        price=Decimal("20.50"),
    )

    t2 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-001"),
        datetime=datetime(2023, 12, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("65.23"),
    )

    t3 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-001"),
        datetime=datetime(2024, 1, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("65.23"),
    )

    t4 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-001"),
        datetime=datetime(2024, 2, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=3,
        price=Decimal("65.23"),
    )

    t5 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-001"),
        datetime=datetime(2024, 3, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=3,
        price=Decimal("65.23"),
    )


    # AR-MALB-003: 1 purchase (14) + 2 sales (10,16)
    t6 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-003"),
        datetime=datetime(2024, 4, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=14,
        price=Decimal("9.00"),
    )

    t7 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-003"),
        datetime=datetime(2024, 5, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=10,
        price=Decimal("18.00"),
    )

    t8 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-MALB-003"),
        datetime=datetime(2024, 6, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=16,
        price=Decimal("18.00"),
    )


    # AR-TORR-001: 2 purchases (10,11) + 2 sales (9,11)
    t9 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-TORR-001"),
        datetime=datetime(2024, 7, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=10,
        price=Decimal("9.50"),
    )

    t10 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-TORR-001"),
        datetime=datetime(2024, 8, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=11,
        price=Decimal("9.50"),
    )

    t11 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-TORR-001"),
        datetime=datetime(2024, 9, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("17.00"),
    )

    t12 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-TORR-001"),
        datetime=datetime(2024, 10, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=11,
        price=Decimal("17.00"),
    )


    # AR-WHITE-001 — 2 sales (8,9)
    t13 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-WHITE-001"),
        datetime=datetime(2024, 11, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=8,
        price=Decimal("15.00"),
    )

    t14 = StockMovement(
        wine=Wine.get_by_filter(session, code="AR-WHITE-001"),
        datetime=datetime(2024, 12, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("15.00"),
    )


    # AU-RED-001 — 1 purchase (19) + 2 sales (7,8)
    t15 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-RED-001"),
        datetime=datetime(2025, 1, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=19,
        price=Decimal("28.00"),
    )

    t16 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-RED-001"),
        datetime=datetime(2025, 2, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=7,
        price=Decimal("55.00"),
    )

    t17 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-RED-001"),
        datetime=datetime(2025, 3, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=8,
        price=Decimal("55.00"),
    )


    # AU-RED-002 — 1 purchase (11) + 2 sales (15,19)
    t18 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-RED-002"),
        datetime=datetime(2025, 4, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=11,
        price=Decimal("7.00"),
    )

    t19 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-RED-002"),
        datetime=datetime(2025, 5, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=15,
        price=Decimal("13.00"),
    )

    t20 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-RED-002"),
        datetime=datetime(2025, 6, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=19,
        price=Decimal("13.00"),
    )


    # AU-WHITE-001 — 1 purchase (5) + 2 sales (20,18)
    t21 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-WHITE-001"),
        datetime=datetime(2025, 7, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=5,
        price=Decimal("9.00"),
    )

    t22 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-WHITE-001"),
        datetime=datetime(2025, 8, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=20,
        price=Decimal("16.00"),
    )

    t23 = StockMovement(
        wine=Wine.get_by_filter(session, code="AU-WHITE-001"),
        datetime=datetime(2025, 9, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=18,
        price=Decimal("16.00"),
    )


    # CL-CABS-001 — 1 purchase (6) + 3 sales (2,2,2)
    t24 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-CABS-001"),
        datetime=datetime(2025, 10, 5, 10, 0, 0),
        transaction_type="purchase",
        quantity=6,
        price=Decimal("30.00"),
    )

    t25 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-CABS-001"),
        datetime=datetime(2025, 11, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("55.00"),
    )

    t26 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-CABS-001"),
        datetime=datetime(2025, 12, 5, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("55.00"),
    )

    t27 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-CABS-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("55.00"),
    )


    # CL-RED-002: 1 purchase (5) + 2 sales (7,7)
    t28 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=5,
        price=Decimal("7.00"),
    )

    t29 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=7,
        price=Decimal("13.00"),
    )

    t30 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=7,
        price=Decimal("13.00"),
    )


    # CL-RED-003: 1 purchase (8) + 2 sales (13,15)
    t31 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=8,
        price=Decimal("9.00"),
    )

    t32 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=13,
        price=Decimal("17.00"),
    )

    t33 = StockMovement(
        wine=Wine.get_by_filter(session, code="CL-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=15,
        price=Decimal("17.00"),
    )


    # ES-FORT-001: 1 purchase (14) + 2 sales (13,13)
    t34 = StockMovement(
        wine=Wine.get_by_filter(session, code="ES-FORT-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=14,
        price=Decimal("11.00"),
    )

    t35 = StockMovement(
        wine=Wine.get_by_filter(session, code="ES-FORT-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=13,
        price=Decimal("20.00"),
    )

    t36 = StockMovement(
        wine=Wine.get_by_filter(session, code="ES-FORT-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=13,
        price=Decimal("20.00"),
    )


    # ES-RED-002: 1 purchase (11) + 2 sales (5,7)
    t37 = StockMovement(
        wine=Wine.get_by_filter(session, code="ES-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=11,
        price=Decimal("18.00"),
    )

    t38 = StockMovement(
        wine=Wine.get_by_filter(session, code="ES-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=5,
        price=Decimal("32.00"),
    )

    t39 = StockMovement(
        wine=Wine.get_by_filter(session, code="ES-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=7,
        price=Decimal("32.00"),
    )


    # FR-RED-003: 2 purchases (120,11) + 2 sales (4,6) — única cantidad de 3 dígitos
    t40 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=120,
        price=Decimal("65.00"),
    )

    t41 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=11,
        price=Decimal("65.00"),
    )

    t42 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=4,
        price=Decimal("22.00"),
    )

    t43 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-RED-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=6,
        price=Decimal("22.00"),
    )


    # FR-ROSE-002: 1 purchase (17) + 2 sales (7,9)
    t44 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-ROSE-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=17,
        price=Decimal("15.00"),
    )

    t45 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-ROSE-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=7,
        price=Decimal("27.00"),
    )

    t46 = StockMovement(
        wine=Wine.get_by_filter(session, code="FR-ROSE-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("27.00"),
    )


    # IT-RED-002: 1 purchase (8) + 2 sales (2,2)
    t47 = StockMovement(
        wine=Wine.get_by_filter(session, code="IT-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=8,
        price=Decimal("65.00"),
    )

    t48 = StockMovement(
        wine=Wine.get_by_filter(session, code="IT-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("120.00"),
    )

    t49 = StockMovement(
        wine=Wine.get_by_filter(session, code="IT-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=2,
        price=Decimal("120.00"),
    )


    # IT-SPAR-001: 1 purchase (8) + 2 sales (8,9)
    t50 = StockMovement(
        wine=Wine.get_by_filter(session, code="IT-SPAR-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=8,
        price=Decimal("9.00"),
    )

    t51 = StockMovement(
        wine=Wine.get_by_filter(session, code="IT-SPAR-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=8,
        price=Decimal("16.00"),
    )

    t52 = StockMovement(
        wine=Wine.get_by_filter(session, code="IT-SPAR-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("16.00"),
    )


    # NZ-WHITE-002: 3 sales (3,4,4)
    t53 = StockMovement(
        wine=Wine.get_by_filter(session, code="NZ-WHITE-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=3,
        price=Decimal("21.00"),
    )

    t54 = StockMovement(
        wine=Wine.get_by_filter(session, code="NZ-WHITE-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=4,
        price=Decimal("21.00"),
    )

    t55 = StockMovement(
        wine=Wine.get_by_filter(session, code="NZ-WHITE-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=4,
        price=Decimal("21.00"),
    )


    # PT-PORT-001 — 1 purchase (9) + 2 sales (4,5)
    t56 = StockMovement(
        wine=Wine.get_by_filter(session, code="PT-PORT-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=9,
        price=Decimal("14.00"),
    )

    t57 = StockMovement(
        wine=Wine.get_by_filter(session, code="PT-PORT-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=4,
        price=Decimal("25.00"),
    )

    t58 = StockMovement(
        wine=Wine.get_by_filter(session, code="PT-PORT-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=5,
        price=Decimal("25.00"),
    )


    # PT-PORT-003: 1 purchase (17) + 2 sales (3,3)
    t59 = StockMovement(
        wine=Wine.get_by_filter(session, code="PT-PORT-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=17,
        price=Decimal("15.00"),
    )

    t60 = StockMovement(
        wine=Wine.get_by_filter(session, code="PT-PORT-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=3,
        price=Decimal("27.00"),
    )

    t61 = StockMovement(
        wine=Wine.get_by_filter(session, code="PT-PORT-003"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=3,
        price=Decimal("27.00"),
    )


    # US-RED-001 — 1 purchase (10) + 2 sales (8,8)
    t62 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-RED-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=10,
        price=Decimal("5.00"),
    )

    t63 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-RED-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=8,
        price=Decimal("9.50"),
    )

    t64 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-RED-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=8,
        price=Decimal("9.50"),
    )


    # US-RED-002: 3 sales (8,9,9)
    t65 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=8,
        price=Decimal("18.00"),
    )

    t66 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("18.00"),
    )

    t67 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-RED-002"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("18.00"),
    )


    # US-ROSE-001: 1 purchase (17) + 2 sales (9,9)
    t68 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-ROSE-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="purchase",
        quantity=17,
        price=Decimal("6.00"),
    )

    t69 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-ROSE-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("11.00"),
    )

    t70 = StockMovement(
        wine=Wine.get_by_filter(session, code="US-ROSE-001"),
        datetime=datetime(2025, 12, 10, 10, 0, 0),
        transaction_type="sale",
        quantity=9,
        price=Decimal("11.00"),
    )

    session.add_all([
        t1, t2, t3, t4, t5,
        t6, t7, t8, t9, t10, 
        t11, t12, t13, t14,
        t15, t16, t17, t18, 
        t19, t20, t21, t22, 
        t23, t24, t25, t26, 
        t27, t28, t29, t30,
        t31, t32, t33, t34, 
        t35, t36, t37, t38, 
        t39, t40, t41, t42,
        t43, t44, t45, t46,
        t47, t48, t49, t50, 
        t51, t52, t53, t54, 
        t55, t56, t57, t58,
        t59, t60, t61, t62, 
        t63, t64, t65, t66, 
        t67, t68, t69, t70,
    ])
    session.commit()
