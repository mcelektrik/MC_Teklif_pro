from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(Text, nullable=True)
    tax_office = Column(String, nullable=True)
    tax_no = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    
    offers = relationship("Offer", back_populates="customer")

class Offer(Base):
    __tablename__ = "offers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    offer_no = Column(String, unique=True, index=True, nullable=True) # Nullable for drafts
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    currency = Column(String, default="TRY") # TRY, USD, EUR
    include_vat = Column(Boolean, default=True) # KDV Dahil mi?
    
    sub_total = Column(Float, default=0.0)
    discount_total = Column(Float, default=0.0)
    vat_total = Column(Float, default=0.0)
    grand_total = Column(Float, default=0.0)
    
    status = Column(String, default="DRAFT") # DRAFT, PUBLISHED
    note = Column(Text, nullable=True)
    
    customer = relationship("Customer", back_populates="offers")
    items = relationship("OfferItem", back_populates="offer", cascade="all, delete-orphan")

class OfferItem(Base):
    __tablename__ = "offer_items"
    
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"))
    
    description = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="Adet")
    unit_price = Column(Float, default=0.0)
    vat_rate = Column(Float, default=20.0) # %20 default
    discount_percent = Column(Float, default=0.0)
    
    total_price = Column(Float, default=0.0) # Calculated
    
    offer = relationship("Offer", back_populates="items")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    stock_code = Column(String(64), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    unit = Column(String(32), nullable=False, default="Adet")
    vat_rate = Column(Float, nullable=False, default=20.0)
    currency = Column(String(8), nullable=False, default="TRY")
    sale_price = Column(Float, nullable=False, default=0.0)

    buy_price = Column(Float, nullable=True)
    barcode = Column(String(64), nullable=True)
    description = Column(Text, nullable=True)
    min_stock = Column(Float, nullable=True, default=0.0)
class AppConfig(Base):
    __tablename__ = "app_config"
    
    key = Column(String, primary_key=True)
    value = Column(String, nullable=True)
