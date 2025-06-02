from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class ReceiptFile(Base):
    __tablename__ = "receipt_file"
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    is_valid = Column(Boolean, default=None)
    invalid_reason = Column(String, default=None)
    is_processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Receipt(Base):
    __tablename__ = "receipt"
    id = Column(Integer, primary_key=True, autoincrement=True)
    purchased_at = Column(DateTime, default=None)
    merchant_name = Column(String, default=None)
    total_amount = Column(Float, default=None)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)