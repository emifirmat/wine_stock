from sqlalchemy import (event, create_engine, Column, ForeignKey, Integer, 
    String, DateTime, Date)
from sqlalchemy.orm import sessionmaker, relationship, declarative_base


# Global variables
MAX_CHARS = 100

# Create connection with sqlite db. Echo=True == debugging mode
engine = create_engine("sqlite:///wineshop.db", echo=True)
# Add event listener to activate Foreing Keys in SQLite (it allows using ondelete)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# Create tables
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
            instance = cls(name="Default Shop", logo_path="") # Empty instance
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
    varietal_id = Column(Integer, ForeignKey("varietal.id", ondelete="SET NULL"))
    vintage_year = Column(Integer, nullable=False)
    origin = Column(String(MAX_CHARS)) # Optional
    code = Column(String, nullable=False)
    wine_picture_path = Column(String) # Optional
    colour = relationship("Colour", back_populates="wines") 
    style = relationship("Style", back_populates="wines") 
    varietal = relationship("Varietal", back_populates="wines", passive_deletes=True) 

class Colour(Base):
    """
    Colour table, contain colour name of the wine
    """
    __tablename__ = "colour"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    wines = relationship("Wine", back_populates="colour")

class Style(Base):
    """
    Style table, contain style name of the wine
    """
    __tablename__ = "style"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    wines = relationship("Wine", back_populates="style")

class Varietal(Base):
    """
    Varietal table, contain varietal name of the main grape which is the wine is 
    produced.
    """
    __tablename__ = "varietal"
    id = Column(Integer, primary_key=True)
    name = Column(String(MAX_CHARS), nullable=False)
    wines = relationship("Wine", back_populates="varietal")
    
Base.metadata.create_all(engine)

# Start session for command operations
Session = sessionmaker(bind=engine)
    

