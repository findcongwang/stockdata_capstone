from sqlalchemy import create_engine
from sqlalchemy import (
    Table, Column, Integer, String, Float,
    Date, DateTime, 
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///stockdata.db', echo = True)
Base = declarative_base()


## --- Universe Models ---
class Asset(Base):
   __tablename__ = 'asset'
   id = Column(Integer, primary_key=True)
   name = Column(String)
   symbol = Column(String)
   asset_type = Column(String)


## --- Price Data Models ---
class Candlestick1M(Base):
   __tablename__ = 'candlestick_1m'
   asset_id = Column(Integer, ForeignKey('asset.id'), primary_key=True)
   timestamp = Column(DateTime, primary_key=True)
   open = Column(Float, nullable=False)
   high = Column(Float, nullable=False)
   low = Column(Float, nullable=False)
   close = Column(Float, nullable=False)
   volume = Column(Integer, nullable=False)


class Candlestick1H(Base):
   __tablename__ = 'candlestick_1h'
   asset_id = Column(Integer, ForeignKey('asset.id'), primary_key=True)
   timestamp = Column(DateTime, primary_key=True)
   open = Column(Float, nullable=False)
   high = Column(Float, nullable=False)
   low = Column(Float, nullable=False)
   close = Column(Float, nullable=False)
   volume = Column(Integer, nullable=False)


class Candlestick1D(Base):
   __tablename__ = 'candlestick_1d'
   asset_id = Column(Integer, ForeignKey('asset.id'), primary_key=True)
   timestamp = Column(DateTime, primary_key=True)
   open = Column(Float, nullable=False)
   high = Column(Float, nullable=False)
   low = Column(Float, nullable=False)
   close = Column(Float, nullable=False)
   volume = Column(Integer, nullable=False)


## --- Fundamental Data Models ---
class FinancialReport(Base):
   __tablename__ = 'financial_report'
   id = Column(Integer, primary_key=True)
   asset_id = Column(Integer, ForeignKey('asset.id'))
   simfin_id = Column(String)
   fiscal_period = Column(String)
   fiscal_year = Column(Integer)
   report_date = Column(Date)
   publish_date = Column(Date)
   restated_date = Column(Date)
   source = Column(String)
   simfin_uniq = UniqueConstraint('simfin_id', name='simfin_idx')


class ProfitLossReportData(Base):
   id = Column(Integer, primary_key=True)
   financial_report_id = Column(Integer, ForeignKey('financial_report.id'), primary_key=True)


class BalanceSheetReportData(Base):
   id = Column(Integer, primary_key=True)
   financial_report_id = Column(Integer, ForeignKey('financial_report.id'), primary_key=True)


class CashFlowReportData(Base):
   id = Column(Integer, primary_key=True)
   financial_report_id = Column(Integer, ForeignKey('financial_report.id'), primary_key=True)


class DerivedReportData(Base):
   id = Column(Integer, primary_key=True)
   financial_report_id = Column(Integer, ForeignKey('financial_report.id'), primary_key=True)


Base.metadata.create_all(engine)
