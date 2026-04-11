from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class DeviceType(str, enum.Enum):
    laptop = "laptop"
    phone = "phone"
    other = "other"

class DeviceStatus(str, enum.Enum):
    in_stock = "stokta"
    assigned = "atanmis"
    maintenance = "bakimda"
    retired = "hurda"

class RequestStatus(str, enum.Enum):
    pending = "beklemede"
    approved = "onaylandi"
    shipped = "gonderildi"
    rejected = "reddedildi"

class Person(Base):
    __tablename__ = "persons"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    meta = Column(JSON, nullable=True) # Ekstra bilgiler için (tel, adres vb.)
    requests = relationship("Request", back_populates="person")

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    inventory_code = Column(String, unique=True, nullable=True, index=True)
    device_type = Column(String, nullable=False) # laptop / phone
    brand = Column(String, nullable=False)
    model = Column(String, nullable=False)
    serial_no = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, default=DeviceStatus.in_stock)
    specs = Column(JSON, nullable=True) # Laptop RAM/CPU veya Telefon Depolama bilgileri
    assignment = relationship("Assignment", back_populates="device", uselist=False)

class Request(Base):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("persons.id"), nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, default=RequestStatus.pending)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    person = relationship("Person", back_populates="requests")
    assignment = relationship("Assignment", back_populates="request", uselist=False)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("requests.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    tracking_no = Column(String, nullable=True)
    request = relationship("Request", back_populates="assignment")
    device = relationship("Device", back_populates="assignment")
