"""
Database models and ORM definitions.

This module defines all SQLAlchemy models for the wine stock management system,
including Shop, Wine, Colour, Style, Varietal, and StockMovement tables.
Also configures the database engine and session.
"""
from sqlalchemy import (event, create_engine, Column, ForeignKey, Integer, 
    String, DateTime, Numeric, Enum, text, func)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base, validates, Session
from datetime import datetime
from typing import Self

from db.bootstrap import get_sqlalchemy_url

# == Global variables ==
MAX_CHARS = 100

# == DB Connection ==
# Create connection with sqlite db. Echo=True == debugging mode
engine = create_engine(get_sqlalchemy_url(), echo=False)

# == Event Listeners ==
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record) -> None:
    """
    Enable foreign key constraints in SQLite.
    
    SQLite disables foreign keys by default. This event listener
    activates them for every new connection.
    
    Parameters:
        dbapi_connection: Database API connection object
        connection_record: Connection record (not used)
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# == Mixins ==
class NamedModelMixin:
    """
    Mixin for models with a "name" attribute.
    
    Provides common query methods for models that have a name field,
    including ordered retrieval and lookup by name.
    """
    @classmethod
    def all_ordered(cls, session: Session) -> list:
        """
        Get all instances sorted by name (case-insensitive, ascending).
        
        Parameters:
            session: SQLAlchemy database session
            
        Returns:
            List of all model instances ordered alphabetically by name

        """
        return session.query(cls).order_by(func.lower(cls.name).asc()).all()
      
    
    @classmethod
    def get_by_filter(cls, session: Session, **filters) -> Self | None:
        """
        Get a single instance matching the given filters.
        
        Parameters:
            session: SQLAlchemy database session
            **filters: Key-value pairs to filter the query
            
        Returns:
            First matching instance or None
            
        Raises:
            ValueError: If filter is not provided
        """
        if not filters:
            raise ValueError("At least one filter must be provided.")
        return session.query(cls).filter_by(**filters).first()


# == Create tables ==
Base = declarative_base()

class Shop(Base):
    """
    Shop configuration table.
    
    Stores the shop name and logo path displayed in the application.
    Designed as a singleton - only one record should exist.
    """
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    logo_path = Column(String)

    @classmethod
    def get_singleton(cls, session: Session) -> "Shop":
        """
        Get or create the single shop instance.
        
        Ensures only one shop record exists throughout the application.
        Creates a default instance if none exists.
        
        Parameters:
            session: SQLAlchemy database session
            
        Returns:
            The single Shop instance
        """
        instance = session.query(cls).first()
        if not instance:
            # Create default instance
            instance = cls(name="WINE STOCK", logo_path="assets/logos/app_logo.png")
            session.add(instance)
            session.commit()
        return instance

class Wine(Base, NamedModelMixin):
    """
    Wine catalog table.
    
    Stores detailed information about each wine including name, winery,
    characteristics, pricing, and current stock quantity.
    """
    __tablename__ = "wine"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    winery = Column(String(MAX_CHARS), nullable=False)
    colour_id = Column(Integer, ForeignKey("colour.id", ondelete="RESTRICT"), nullable=False)
    style_id = Column(Integer, ForeignKey("style.id", ondelete="RESTRICT"), nullable=False)
    varietal_id = Column(Integer, ForeignKey("varietal.id", ondelete="SET NULL")) # Optional
    vintage_year = Column(Integer, nullable=False) 
    origin = Column(String(MAX_CHARS)) # Optional
    code = Column(String, unique=True, nullable=False)
    picture_path = Column(String) # Optional
    quantity = Column(Integer, default=0, server_default=text("0"))
    min_stock = Column(Integer) # Optional
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    colour = relationship("Colour", back_populates="wines") 
    style = relationship("Style", back_populates="wines") 
    varietal = relationship("Varietal", back_populates="wines", passive_deletes=True) 
    movements = relationship("StockMovement", back_populates="wine")

    # Ordered list
    @classmethod
    def all_ordered(
        cls, session: Session, order_by: str = "name", distinct: str | None = None
    ) -> list["Wine"]:
        """
        Get all wines sorted by specified field (case-insensitive).
        
        Parameters:
            session: SQLAlchemy database session
            order_by: Field name to sort by
            distinct: Field name to apply distinct filter (optional)
            
        Returns:
            List of Wine instances ordered by specified field
            
        Raises:
            ValueError: If order_by or distinct field doesn't exist in the model
        """
        # Validate fields exist in model
        for field in [order_by, distinct]:
            if field and not hasattr(cls, field):
                raise ValueError(
                    f"Field '{field}' doesn't exist in the model {cls.__name__}"
                )
        
        # Build and return query
        query = session.query(cls)
        
        if distinct: # Optional: Unique values
            query.distinct()
            
        return query.order_by(func.lower(getattr(cls, order_by)).asc()).all()

    @classmethod
    def column_ordered(
        cls, session: Session, column: str, order_by: str = "name", 
        distinct: str | None = None
    ) -> list:
        """
        Get a single column from all wines, sorted by specified field.
        
        Parameters:
            session: SQLAlchemy database session
            column: Column name to retrieve
            order_by: Field name to sort by
            distinct: Field name to apply distinct filter (optional)
            
        Returns:
            List of column values ordered by specified field
            
        Raises:
            ValueError: If column, order_by, or distinct field doesn't exist
        """
        # Validate fields exist in model
        for field in [order_by, distinct]:
            if field and not hasattr(cls, field):
                raise ValueError(f"Field '{field}' doesn't exist in the model {cls.__name__}")
        
        # Build and return sorted query
        query = session.query(getattr(cls, column))

        
        if distinct: # Optional: Unique values
            query = query.distinct()
            
        return query.order_by(func.lower(getattr(cls, order_by)).asc()).all()

    @validates("origin")
    def convert_lower(self, key: str, value: str | None) -> str | None:
        """
        Convert origin to title case if provided.
        """
        return value.title() if value else value
    
    @validates("min_stock")
    def convert_none(self, key: str, value: int | str) -> int | None:
        """
        Convert min_stock to integer or None.
        
        Handles cases where value might be an empty string or other non-numeric type.
        """
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
        
        return None

    @property
    def picture_path_display(self) -> str:
        """
        Get wine picture path or 'default.png' if none exists.
        """
        if self.picture_path:
            return self.picture_path
        return "default.png"
    
    
    @property
    def origin_display(self) -> str:
        """
        Get wine origin or "N/A" if none exists.
        """
        return self.origin if self.origin else "N/A"
    
    @property
    def varietal_display(self) -> str:
        """
        Get varietal name or "N/A" if none exists.
        """
        return self.varietal.name if self.varietal else "N/A"
    
    @property
    def min_stock_display(self) -> str:
        """
        Get min stock as string or "N/A" if none exists.
        """
        return "N/A" if self.min_stock is None else str(self.min_stock)
    
    @property
    def min_stock_sort(self) -> int:
        """
        Get min stock value for sorting purposes.
        
        Returns -1 if min_stock is None, ensuring wines without
        minimum stock appear last when sorting in ascending order.
        """
        return self.min_stock if self.min_stock else -1
    
    @property
    def is_below_min_stock(self) -> bool:
        """
        Check if current quantity is below minimum stock level.
        """
        return self.quantity < self.min_stock_sort

class Colour(Base, NamedModelMixin):
    """
    Wine colour table.
    
    Stores wine colour categories (e.g., red, white, rosé).
    """
    __tablename__ = "colour"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    
    # Relationships
    wines = relationship("Wine", back_populates="colour")


class Style(Base, NamedModelMixin):
    """
    Wine style table.
    
    Stores wine style categories (e.g., still, sparkling, fortified).
    """
    __tablename__ = "style"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    
    # Relationships
    wines = relationship("Wine", back_populates="style")


class Varietal(Base, NamedModelMixin):
    """
    Wine varietal table.
    
    Stores grape varietal names used in wines (e.g., Malbec, Cabernet Sauvignon).
    """
    __tablename__ = "varietal"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    
    # Relationships
    wines = relationship("Wine", back_populates="varietal")
    

class StockMovement(Base):
    """
    Stock movement transaction table.
    
    Records all inventory changes from sales and purchases.
    Automatically updates wine quantity through database triggers (see events.py).
    """
    __tablename__ = "stock_movement"
    id = Column(Integer, primary_key=True)
    wine_id = Column(Integer, ForeignKey("wine.id", ondelete="RESTRICT"), nullable=False)
    datetime = Column(
        DateTime, default=lambda: StockMovement.now_without_microseconds(), nullable=False
    )
    transaction_type = Column(
        Enum("sale", "purchase", name="transaction_type_enum"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    # Price is independent and can be base on either purchase or selling price.
    price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    wine = relationship("Wine", back_populates="movements") 

    @staticmethod
    def now_without_microseconds():
        """
        Get current datetime without microseconds for cleaner timestamps.
        """
        return datetime.now().replace(microsecond=0)

    # Ordered list
    @classmethod
    def all_ordered_by_datetime(
        cls, session: Session, filter: str | None = None
    ) -> list["StockMovement"]:
        """
        Get all stock movements sorted by datetime (descending).
        
        Parameters:
            session: SQLAlchemy database session
            filter: Transaction type filter - "sale", "purchase", or None for all
            
        Returns:
            List of StockMovement instances ordered by datetime (newest first)
        """
        query = session.query(cls).order_by(cls.datetime.desc())
        
        if filter:
            return query.filter(cls.transaction_type == filter).all()
        
        return query.all()
    
    @validates("transaction_type")
    def convert_lower(self, key: str, value: str | None) -> str:
        """
        Convert transaction type to lowercase if provided.
        """
        return value.lower() if value else value

# Note: Base.metadata.create_all() is not used - database migrations are handled by Alembic
# Note 2: For exe files it will require to be used

# == Session ==
# Create session factory for database operations
Session = sessionmaker(bind=engine)
    

