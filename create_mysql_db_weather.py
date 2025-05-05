#imports

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Float, Enum, Numeric, ForeignKey
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import MetaData
from sqlalchemy import Index

from sqlalchemy_utils import database_exists, create_database, drop_database

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

import pymysql

import pandas as pd
import datetime as datetime

#create database


engine = create_engine('mysql+pymysql://root:MYSQL.passw0rd@localhost:3306/weather')

if not database_exists(engine.url):
    create_database(engine.url)
    
Base = declarative_base()

# define Location table
# for lat longs I'm using Numeric as it stores exact values while float stores aprox ones. 
# 9 means up to 9 digist in total, 6 means up to 6 decimal places, 
# it will allow values like ±999.999999 — more than enough for coordinates

class Location(Base):
    __tablename__ = 'Location'
    location_id = Column(Integer,primary_key=True)
    latitude = Column(Numeric(9,6))
    longitude = Column(Numeric(9,6))
    city = Column(String(120))
    region = Column(String(120))
    country = Column(String(120))


# define Weather Data table for historical weather data
# autoincrementing so that my future ETL doesn't have to manage the IDs
# using Numeric instead of float for precision

class Weather_Data(Base):
    __tablename__ = 'Weather_Data'

    measurement_id = Column(Integer, primary_key=True, autoincrement=True) 
    location_id = Column(Integer, ForeignKey('Location.location_id'))
    time = Column(Date)

    shortwave_radiation_sum_MJ_m2 = Column(Numeric(6, 3))       # MJ/m²
    temperature_2m_max_C = Column(Numeric(6, 3))                # °C
    precipitation_sum_mm = Column(Numeric(6, 3))                # mm
    relative_humidity_2m_mean_percent = Column(Numeric(5, 2))   # %
    temperature_2m_mean_C = Column(Numeric(6, 3))               # °C
    temperature_2m_min_C = Column(Numeric(6, 3))                # °C

# create BTREE index on time column in Weather_Data table


Index('ix_weather_data_time', Weather_Data.time)

# create Customer table
class Customer(Base):
    __tablename__ = 'Customer'

    customer_id = Column(Integer, primary_key=True)
    customer_name = Column(String(255))
    location_id = Column(Integer, ForeignKey('Location.location_id'))
    safety_risk = Column(Integer)
    difficult_access = Column(Integer)

# create Device Component static small table

class Device_Component(Base):
    __tablename__ = 'Device_Component'

    component_id = Column(Integer, primary_key=True)
    manufacturer = Column(String(255))
    category = Column(String(120))
    device_type = Column(String(120))
    risk_type = Column(String(255))

# create Device table

class Device(Base):
    __tablename__ = 'Device'

    device_id = Column(Integer, primary_key=True)
    component_1 = Column(Integer, ForeignKey('Device_Component.component_id'))
    component_2 = Column(Integer, ForeignKey('Device_Component.component_id'))
    component_3 = Column(Integer, ForeignKey('Device_Component.component_id'))
    location_id = Column(Integer, ForeignKey('Location.location_id'))


# create table
Base.metadata.create_all(engine)




