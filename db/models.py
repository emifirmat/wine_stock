from sqlalchemy import (event, create_engine, Column, ForeignKey, Integer, 
    String, DateTime, Numeric, Enum, text, func)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime


# == Global variables ==
MAX_CHARS = 100

# == DB Connection ==
# Create connection with sqlite db. Echo=True == debugging mode
engine = create_engine("sqlite:///wineshop.db", echo=False)
# Add event listener to activate Foreing Keys in SQLite (it allows using ondelete)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# == Mixins ==
class NamedModelMixin:
    
    @classmethod
    def all_ordered(cls, session):
        """
        Sorts the instances obtained from a query in asceding order case 
        insensitive.
            - query(cls).all(): returns all the results from the query on table cls.
            - order_by(cls.name).asc(): sorts the results of the query by the name 
            attribute in ascending order.
            - func.lower(cls.name): makes the attribute name lower case (used to
            add case insensitive capalities to the query).

        """
        return session.query(cls).order_by(func.lower(cls.name)).asc().all()
    
    @classmethod
    def get_name(cls, session, **filters):
        """
        Return the instance or create a new one.

        Inputs:
            session: DB session to make query
            **filters: Key-pair values used to filter the query
        """
        if not filters["name"]:
            raise ValueError("Attribute 'name' should have a value.")
        return session.query(cls).filter_by(**filters).first()


# == Create tables ==
Base = declarative_base()

class Shop(Base):
    """
    Shop table, contains name and logo path of the shop.
    """
    __tablename__ = "shop"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    logo_path = Column(String)

    @classmethod
    def get_singleton(cls, session) -> "Shop":
        """
        Centralises access to the table with the objective of ensuring that only
        one shop record is used throughout the application.
        Inputs:
            - session: SQLAlchemy session object connectEd to the db
        Returns:
            - The single shop instance
        """
        instance = session.query(cls).first()
        if not instance:
            # Default instance
            instance = cls(name="WINE STOCK", logo_path="assets/logos/app_logo.png")
            session.add(instance)
            session.commit()
        return instance

class Wine(Base):
    """
    Wine table, contain details of the wine.
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
    purchase_price = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)

    # Relationships
    colour = relationship("Colour", back_populates="wines") 
    style = relationship("Style", back_populates="wines") 
    varietal = relationship("Varietal", back_populates="wines", passive_deletes=True) 
    movements = relationship("StockMovement", back_populates="wine", cascade="all, delete")

    # Ordered list
    @classmethod
    def all_ordered(cls, session, order_by="name", distinct=None):
        # Check order_by has the correct field
        
        for field in [order_by, distinct]:
            if field and not hasattr(cls, field):
                raise ValueError(f"Field {field} doesn't exist in the model {cls.__name__}")
        
        # Return sorted query
        if distinct: # Unique values
            return session.query(cls)\
                .distinct()\
                .order_by(func.lower(getattr(cls, order_by)).asc())\
                .all()
        else: # Values can be repeated
            return session.query(cls)\
                .order_by(func.lower(getattr(cls, order_by)).asc())\
                .all()

    @classmethod
    def column_ordered(cls, session, column, order_by="name", distinct=None):
        # Check order_by has the correct field
        for field in [order_by, distinct]:
            if field and not hasattr(cls, field):
                raise ValueError(f"Field {field} doesn't exist in the model {cls.__name__}")
        
        # Return sorted query
        if distinct: # Unique values
            return session.query(getattr(cls, column))\
                .distinct()\
                .order_by(func.lower(getattr(cls, order_by)).asc())\
                .all()
        else: # Values can be repeated
            return session.query(getattr(cls, column))\
                .order_by(func.lower(getattr(cls, order_by)).asc())\
                .all()

    @property
    def picture_path_display(self):
        """
        Displays the origin of the wine or N/A.
        """
        if self.picture_path:
            return self.picture_path
        else:
            return "assets/user_images/wines/default_wine.png"
    
    
    @property
    def origin_display(self):
        """
        Displays the origin of the wine or N/A.
        """
        return self.origin if self.origin else "N/A"
    
    @property
    def varietal_display(self):
        """
        Displays the varietal name of the wine or N/A.
        """
        return self.varietal.name if self.varietal else "N/A"
       
    

class Colour(Base, NamedModelMixin):
    """
    Colour table, contains colour name of the wine
    """
    __tablename__ = "colour"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    
    # Relationships
    wines = relationship("Wine", back_populates="colour")


class Style(Base, NamedModelMixin):
    """
    Style table, contains style name of the wine
    """
    __tablename__ = "style"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    
    # Relationships
    wines = relationship("Wine", back_populates="style")


class Varietal(Base, NamedModelMixin):
    """
    Varietal table, contains varietal name of the main grape used for the wine.
    """
    __tablename__ = "varietal"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    
    # Relationships
    wines = relationship("Wine", back_populates="varietal")
    

class StockMovement(Base):
    """
    Stock Movement table, contains any stock movement generated by a selling or 
    purchase
    """
    __tablename__ = "stock_movement"
    id = Column(Integer, primary_key=True)
    wine_id = Column(Integer, ForeignKey("wine.id", ondelete="CASCADE"), nullable=False)
    datetime = Column(DateTime, default=datetime.now, nullable=False)
    transaction_type = Column(
        Enum("sale", "purchase", name="transaction_type_enum"), nullable=False
    )
    quantity = Column(Integer, nullable=False)
    # Price is independent and can be base on either the purchase or selling price.
    price = Column(Numeric(10, 2), nullable=False)
    
    # Relationships
    wine = relationship("Wine", back_populates="movements") 

    # Ordered list
    @classmethod
    def all_ordered(cls, session, filter: str = None):
        """
        Returns a list ordered by datetime in desc order.

        Inputs:
            filter: Returns a filtered version of the list.
        """
        ordered_list = session.query(cls).order_by(cls.datetime.desc())
        
        if filter:
            return ordered_list.filter(cls.transaction_type == filter).all()
        
        return ordered_list.all()

 
Base.metadata.create_all(engine)

# == Session ==
# Start session for command operations
Session = sessionmaker(bind=engine)
    

