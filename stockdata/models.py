import os
from dotenv import load_dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, sessionmaker

from sqlalchemy import (
    Table, Column, Integer, String, Float,
    Date, DateTime, 
    ForeignKey, UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base

DB_CONNECTION = os.environ.get("DB_CONNECTION")
engine = create_engine(DB_CONNECTION, echo = True)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()


## --- Universe Models ---
class Asset(Base):
    __tablename__ = 'asset'
    id = Column(Integer, primary_key=True)
    name = Column(String)                               # name of the asset / corporation
    symbol = Column(String)                             # unique identifier and ticker
    asset_type = Column(String)                         # type, one of stock / forex
    
    # constriants
    asset_uniq = UniqueConstraint('symbol', name='asset_name_uniq')

    # relationships
    candlestick_1m = relationship("Candlestick1M", back_populates="asset")
    candlestick_1h = relationship("Candlestick1H", back_populates="asset")
    candlestick_1d = relationship("Candlestick1D", back_populates="asset")
    financial_reports = relationship("FinancialReport", back_populates="asset")


## --- Price Data Models ---
class Candlestick1M(Base):
    __tablename__ = 'candlestick_1m'
    asset_id = Column(Integer, ForeignKey('asset.id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)      # timestamp of the candlestick
    open = Column(Float, nullable=False)                # opening price
    high = Column(Float, nullable=False)                # highest price in the duration
    low = Column(Float, nullable=False)                 # lowest price in the duration
    close = Column(Float, nullable=False)               # closing price
    volume = Column(Integer, nullable=False)            # total volume in the duration
    asset = relationship("Asset", back_populates="candlestick_1m")


class Candlestick1H(Base):
    __tablename__ = 'candlestick_1h'
    asset_id = Column(Integer, ForeignKey('asset.id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    asset = relationship("Asset", back_populates="candlestick_1h")


class Candlestick1D(Base):
    __tablename__ = 'candlestick_1d'
    asset_id = Column(Integer, ForeignKey('asset.id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    asset = relationship("Asset", back_populates="candlestick_1d")


## --- Fundamental Data Models ---
class FinancialReport(Base):
    __tablename__ = 'financial_report'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('asset.id'))
    simfin_id = Column(String, nullable=False)          # SimFin uniq report id
    fiscal_period = Column(String, nullable=False)      # Fiscal Period, one of [Q1, Q2, Q3, Q4]
    fiscal_year = Column(Integer, nullable=False)       # Fiscal Year
    report_date = Column(Date, nullable=False)          # Report Date
    publish_date = Column(Date, nullable=False)         # Published Date
    restated_date = Column(Date, nullable=False)        # Restated Date (i.e. revision)
    source = Column(String, nullable=False)             # Source document URI

    # constriants
    simfin_id_uniq = UniqueConstraint('simfin_id', name='simfin_id_uniq')

    # relationships
    asset = relationship("Asset", back_populates="financial_reports")
    profit_loss = relationship("ProfitLossReportData", back_populates="financial_report")
    balance_sheet = relationship("BalanceSheetReportData", back_populates="financial_report")
    cash_flow = relationship("CashFlowReportData", back_populates="financial_report")
    derived_data = relationship("DerivedReportData", back_populates="financial_report")

    @staticmethod
    def simfin_property_lookup():
        return {
            "simfin_id": "SimFinId",
            "fiscal_period": "Fiscal Period",
            "fiscal_year": "Fiscal Year",
            "report_date": "Report Date",
            "publish_date": "Publish Date",
            "restated_date": "Restated Date",
            "source": "Source",
        }


class ProfitLossReportData(Base):
    __tablename__ = 'profit_loss_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))

    revenue = Column(Float)                             # "Revenue"
    cost_revenue = Column(Float)                        # "Cost of Revenue"
    gross_profit = Column(Float)                        # "Gross Profit"
    operating_expenses = Column(Float)                  # "Operating Expenses"
    operating_income_loss = Column(Float)               # "Operating Income (Loss)"
    non_operating_income_loss = Column(Float)           # "Non-Operating Income (Loss)"
    other_non_operating_income_loss = Column(Float)     # "Other Non-Operating Income (Loss)"
    pretax_income_adj = Column(Float)                   # "Pretax Income (Loss) Adj."
    pretax_income = Column(Float)                       # "Pretax Income (Loss)"
    income_tax_expense_net = Column(Float)              # "Income Tax (Expense) Benefit Net"
    net_income = Column(Float)                          # "Net Income"
    net_income_common = Column(Float)                   # "Net Income (Common)"
    financial_report = relationship("FinancialReport", back_populates="profit_loss")

    @staticmethod
    def simfin_property_lookup():
        return {
            "revenue": "Revenue",
            "cost_revenue": "Cost of Revenue",
            "gross_profit": "Gross Profit",
            "operating_expenses": "Operating Expenses",
            "operating_income_loss": "Operating Income (Loss)",
            "non_operating_income_loss": "Non-Operating Income (Loss)",
            "other_non_operating_income_loss": "Other Non-Operating Income (Loss)",
            "pretax_income_adj": "Pretax Income (Loss) Adj.",
            "pretax_income": "Pretax Income (Loss)",
            "income_tax_expense_net": "Income Tax (Expense) Benefit Net",
            "net_income": "Net Income",
            "net_income_common": "Net Income (Common)",
        }


class BalanceSheetReportData(Base):
    __tablename__ = 'balance_sheet_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))

    # "Cash, Cash Equivalents & Short Term Investments"
    cash_equivalents_st_investments = Column(Float)    
    cash_equivalents = Column(Float)                    # "Cash & Cash Equivalents"
    st_investments = Column(Float)                      # "Short Term Investments"
    accounts_receivable = Column(Float)                 # "Accounts & Notes Receivable"
    accounts_receivable_net = Column(Float)             # "Accounts Receivable Net"
    inventories = Column(Float)                         # "Inventories"
    other_st_assets = Column(Float)                     # "Other Short Term Assets"
    misc_st_assets = Column(Float)                      # "Misc. Short Term Assets"
    total_current_assets = Column(Float)                # "Total Current Assets"
    property_equipment_net = Column(Float)              # "Property Plant & Equipment Net"
    lt_investments = Column(Float)                      # "Long Term Investments & Receivables"
    other_lt_assets = Column(Float)                     # "Other Long Term Assets"
    misc_lt_assets = Column(Float)                      # "Misc. Long Term Assets"
    toal_noncurrent_assets = Column(Float)              # "Total Noncurrent Assets"
    total_assets = Column(Float)                        # "Total Assets"
    payables_accurals = Column(Float)                   # "Payables & Accruals"
    accounts_payable = Column(Float)                    # "Accounts Payable"
    st_debt = Column(Float)                             # "Short Term Debt"
    other_st_liabilities = Column(Float)                # "Other Short Term Liabilities"
    deferred_revenue = Column(Float)                    # "Deferred Revenue (Short Term)"
    misc_st_liabilities = Column(Float)                 # "Misc. Short Term Liabilities"
    totoal_current_liabilities = Column(Float)          # "Total Current Liabilities"
    lt_debt = Column(Float)                             # "Long Term Debt"
    other_lt_liabilities = Column(Float)                # "Other Long Term Liabilities"
    misc_lt_liabilities = Column(Float)                 # "Misc. Long Term Liabilities"
    total_noncurrent_liabilities = Column(Float)        # "Total Noncurrent Liabilities"
    total_liabilities = Column(Float)                   # "Total Liabilities"
    share_add_capital = Column(Float)                   # "Share Capital & Additional Paid-In Capital"
    retained_earnings = Column(Float)                   # "Retained Earnings"
    other_equity = Column(Float)                        # "Other Equity"
    equity_before_minority_interest = Column(Float)     # "Equity Before Minority Interest"
    total_equity = Column(Float)                        # "Total Equity"
    total_liabilities_equity = Column(Float)            # "Total Liabilities & Equity"
    financial_report = relationship("FinancialReport", back_populates="balance_sheet")

    @staticmethod
    def simfin_property_lookup():
        return {
            "cash_equivalents_st_investments": "Cash, Cash Equivalents & Short Term Investments",
            "cash_equivalents": "Cash & Cash Equivalents",
            "st_investments": "Short Term Investments",
            "accounts_receivable": "Accounts & Notes Receivable",
            "accounts_receivable_net": "Accounts Receivable Net",
            "inventories": "Inventories",
            "other_st_assets": "Other Short Term Assets",
            "misc_st_assets": "Misc. Short Term Assets",
            "total_current_assets": "Total Current Assets",
            "property_equipment_net": "Property Plant & Equipment Net",
            "lt_investments": "Long Term Investments & Receivables",
            "other_lt_assets": "Other Long Term Assets",
            "misc_lt_assets": "Misc. Long Term Assets",
            "toal_noncurrent_assets": "Total Noncurrent Assets",
            "total_assets": "Total Assets",
            "payables_accurals": "Payables & Accruals",
            "accounts_payable": "Accounts Payable",
            "st_debt": "Short Term Debt",
            "other_st_liabilities": "Other Short Term Liabilities",
            "deferred_revenue": "Deferred Revenue (Short Term)",
            "misc_st_liabilities": "Misc. Short Term Liabilities",
            "totoal_current_liabilities": "Total Current Liabilities",
            "lt_debt": "Long Term Debt",
            "other_lt_liabilities": "Other Long Term Liabilities",
            "misc_lt_liabilities": "Misc. Long Term Liabilities",
            "total_noncurrent_liabilities": "Total Noncurrent Liabilities",
            "total_liabilities": "Total Liabilities",
            "share_add_capital": "Share Capital & Additional Paid-In Capital",
            "retained_earnings": "Retained Earnings",
            "other_equity": "Other Equity",
            "equity_before_minority_interest": "Equity Before Minority Interest",
            "total_equity": "Total Equity",
            "total_liabilities_equity": "Total Liabilities & Equity",
        }


class CashFlowReportData(Base):
    __tablename__ = 'cash_flow_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))

    net_income = Column(Float)                    # "Net Income\/Starting Line"
    depreciation_amortization = Column(Float)     # "Depreciation & Amortization"
    non_cash_items = Column(Float)                # "Non-Cash Items"
    change_working_capital = Column(Float)        # "Change in Working Capital"
    net_cash_from_operating = Column(Float)       # "Net Cash from Operating Activities"
    change_in_fixed_assets = Column(Float)        # "Change in Fixed Assets & Intangibles"
    acquisition_fixed_assets = Column(Float)      # "Acquisition of Fixed Assets & Intangibles"
    net_change_lt_investment = Column(Float)      # "Net Change in Long Term Investment"
    decrease_lt_investment = Column(Float)        # "Decrease in Long Term Investment"
    increase_lt_investment = Column(Float)        # "Increase in Long Term Investment"
    net_cash_acquisitions = Column(Float)         # "Net Cash from Acquisitions & Divestitures"
    other_investing_activities = Column(Float)    # "Other Investing Activities"
    net_cash_investing_activies = Column(Float)   # "Net Cash from Investing Activities"
    dividents_paid = Column(Float)                # "Dividends Paid"
    cash_from_debt = Column(Float)                # "Cash from (Repayment of) Debt"
    cash_from_dt_debt_net = Column(Float)         # "Cash from (Repayment of) Short Term Debt Net"
    cash_from_equity = Column(Float)              # "Cash from (Repurchase of) Equity"
    increase_capital_stock = Column(Float)        # "Increase in Capital Stock"
    decrease_capital_stock = Column(Float)        # "Decrease in Capital Stock"
    other_financing_activities = Column(Float)    # "Other Financing Activities"
    net_cash_financing_activities = Column(Float) # "Net Cash from Financing Activities"
    net_cash_before_op_forex = Column(Float)      # "Net Cash Before Disc. Operations and FX"
    net_cash_before_fx = Column(Float)            # "Net Cash Before FX"
    net_cash_in_cash = Column(Float)              # "Net Change in Cash"
    financial_report = relationship("FinancialReport", back_populates="cash_flow")

    @staticmethod
    def simfin_property_lookup():
        return {
            "net_income": "Net Income\/Starting Line",
            "depreciation_amortization": "Depreciation & Amortization",
            "non_cash_items": "Non-Cash Items",
            "change_working_capital": "Change in Working Capital",
            "net_cash_from_operating": "Net Cash from Operating Activities",
            "change_in_fixed_assets": "Change in Fixed Assets & Intangibles",
            "acquisition_fixed_assets": "Acquisition of Fixed Assets & Intangibles",
            "net_change_lt_investment": "Net Change in Long Term Investment",
            "decrease_lt_investment": "Decrease in Long Term Investment",
            "increase_lt_investment": "Increase in Long Term Investment",
            "net_cash_acquisitions": "Net Cash from Acquisitions & Divestitures",
            "other_investing_activities": "Other Investing Activities",
            "net_cash_investing_activies": "Net Cash from Investing Activities",
            "dividents_paid": "Dividends Paid",
            "cash_from_debt": "Cash from (Repayment of) Debt",
            "cash_from_dt_debt_net": "Cash from (Repayment of) Short Term Debt Net",
            "cash_from_equity": "Cash from (Repurchase of) Equity",
            "increase_capital_stock": "Increase in Capital Stock",
            "decrease_capital_stock": "Decrease in Capital Stock",
            "other_financing_activities": "Other Financing Activities",
            "net_cash_financing_activities": "Net Cash from Financing Activities",
            "net_cash_before_op_forex": "Net Cash Before Disc. Operations and FX",
            "net_cash_before_fx": "Net Cash Before FX",
            "net_cash_in_cash": "Net Change in Cash",
        }


class DerivedReportData(Base):
    __tablename__ = 'derived_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))

    ebitda = Column(Float)                      # "EBITDA"
    total_debt = Column(Float)                  # "Total Debt"
    free_cash_flow = Column(Float)              # "Free Cash Flow"
    gross_profit_margin = Column(Float)         # "Gross Profit Margin"
    operating_margin = Column(Float)            # "Operating Margin"
    net_profit_marge = Column(Float)            # "Net Profit Margin"
    return_on_equity = Column(Float)            # "Return on Equity"
    return_on_assets = Column(Float)            # "Return on Assets"
    free_cash_flow_net = Column(Float)          # "Free Cash Flow to Net Income"
    current_ratio = Column(Float)               # "Current Ratio"
    liabilities_equity_ratio = Column(Float)    # "Liabilities to Equity Ratio"
    debt_ratio = Column(Float)                  # "Debt Ratio"
    earnings_per_share_basic = Column(Float)    # "Earnings Per Share Basic"
    earnings_per_share_diluted = Column(Float)  # "Earnings Per Share Diluted"
    sales_per_share = Column(Float)             # "Sales Per Share"
    equity_per_share = Column(Float)            # "Equity Per Share"
    free_cash_flow_per_share = Column(Float)    # "Free Cash Flow Per Share"
    dividends_per_share = Column(Float)         # "Dividends Per Share"
    pietroski_f_score = Column(Float)           # "Pietroski F-Score"
    financial_report = relationship("FinancialReport", back_populates="derived_data")

    @staticmethod
    def simfin_property_lookup():
        return {
            "ebitda": "EBITDA",
            "total_debt": "Total Debt",
            "free_cash_flow": "Free Cash Flow",
            "gross_profit_margin": "Gross Profit Margin",
            "operating_margin": "Operating Margin",
            "net_profit_marge": "Net Profit Margin",
            "return_on_equity": "Return on Equity",
            "return_on_assets": "Return on Assets",
            "free_cash_flow_net": "Free Cash Flow to Net Income",
            "current_ratio": "Current Ratio",
            "liabilities_equity_ratio": "Liabilities to Equity Ratio",
            "debt_ratio": "Debt Ratio",
            "earnings_per_share_basic": "Earnings Per Share Basic",
            "earnings_per_share_diluted": "Earnings Per Share Diluted",
            "sales_per_share": "Sales Per Share",
            "equity_per_share": "Equity Per Share",
            "free_cash_flow_per_share": "Free Cash Flow Per Share",
            "dividends_per_share": "Dividends Per Share",
            "pietroski_f_score": "Pietroski F-Score",
        }


def main():
    load_dotenv()
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    main()
