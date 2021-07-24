# Stockdata (Udacity Capstone)

This project collects ticker and fundamental data, and offers the consolidated data to compute various signal events for persistence and analysis. For example, a LSTM neural network to detect trade patterns.

Stockdata is a custom Udacity Data Engineering Nanodegree capstone project. As such, it has corresponding requirements:

### Project Scope
* Ticker data is fetched via AlphaVantage, whereas fundamentals data is fetched from SimFin. Minutely data is fetched for minimally 2 years from an list of stock symbols and roughly equates to about 2 million records per stock ticker.
* The end use cases for the organized data is for quantamental (quantitive + fundamental) analysis. This project builds the source of truth tables for the core data, as well as extended dimensions tables for technical indicators.
* On top of data querys for reseach and analysis, the data is normalized to enable the building of a minutely backtester with corresponding fundamental events (i.e. company earnings report).

### Data Cleanup
* Stock price data are missing on non-trading hours (i.e. after-hours, weekends, holidays), which is expected. The source data is already adjusted for dividends and splits so there is no processing required on that front. However, the API returns csv response that would need to be transformed to store in a relational database.
* SimFin API endpoints provide "dimensions table" queries for various reports and such the "fact table" would need to be inferred and upserted. In additional normalizing data formats.
* Some data entries from SimFin are numeric, while some are strings of the numbers, parseing is required for those entries.
* API limitations: Since the free API access level is used for both AlphaVantage and SimFin, various query complexity and bulk limits apply, the ETL process need to detect missing data and batch queries to only the free-tier API spec.

### How to Run

Copy `env.example` to `.env` and populate it with API keys from Alphavantage and SimFin (both are free). Make sure docker is installed on your system.

```
# install pipenv
pip install pipenv --user

# activate the virtual environment
pipenv shell

# install dependencies
pipenv sync

# start docker container for postgres db
docker-compose up -d

# seed the initial list of assets
python stockdata/seed.py

# fetch candlesticks
python stockdata/utils/alphavantage_loader.py

# fetch fundamentals
python stockdata/utils/simfin_loader.py

# run pytest, all cases should pass
pytest
```

### Data Model

Overall Schema
![general_erd](images/stockdata_erd.png "Stockdata ERD")

Financial report details
![fundaments_erd](images/fundamentals_erd.png "Fundamentals ERD")

### ETL Pipeline
* DAGs are found under `/dags` folder, airflow will be installed after `pipenv sync` in the local virtual environment. Remember to update dags_folder in airflow.cfg to see the dags.
* `update_candlesticks` is scheduled daily
* `update_fundamentals` is scheduled monthly

![etl_design](images/etl_dags_design.png "ETL Design")


### Tech Stack Rationale

Apache Airflow is used to schedule and perform ETL to fetch data from remote sources and keep the data up-to-date. The goal here to gather historical factual data to further analysis, since we want to have flexible queries (for research), a relational database makes sense.

The model was chosen to reflect the nature of the data. I.e. factual occurances for historical prices and financial reports, and additional dimensions of derived data. For example, a star-schema is used for financial reports per company, per quarter.

As the primiary use here is analysis and backtesting (as opposed to live-trading, which would require real-time quotes), a daily update of the pricing data and monthly update of the financial reporting data would suffice to for the use cases.

### Notes on Scaled Scenarios

#### (If the data was increased by 100x.)

We would need to more mindful of the use cases and handle indexing and partitioning to improve performance. However, if the nature of the data increase was a change in the end use case (i.e. from a single-team tools to a service supporting multiple teams), it maybe justify a migration to a NoSQL database like Cassandra.

#### (If the pipelines were run on a daily basis by 7am.)

The pipelines would already be running daily, what's important here is to ensure the ETL script terminates early if no new data is needed, or if the asset list is massive (1000+ tickers), a premium API key would be needed, or better batching of API request would be needed. 

#### (If the database needed to be accessed by 100+ people.)

In this case, we could consider some use case / query optimized tables, or switching to a NoSQL database like Cassandra, and re-design the data model to maximize throughput. The re-modelling in Cassandra would make more sense in conjunction with the data being scaled too, which would mean the project changed from a single-team reseach data bank to a service offered to multiple teams, each with different data usage requirements.

### Sample Queries and Use Cases

#### Fetching hourly data to compute indicators

Users can query either resolution of the data to compute indicators using for example, TA-Lib https://mrjbq7.github.io/ta-lib/

![aapl_hourly](images/get_hourly_candles.png "AAPL Hourly")

#### Simulating report publishing in backtest

Users can query all the details of a financial report (100+ columns when joined) and make the data available only on the report's publish date in a backtest loop.

i.e. for each day, minutely data is queried and stepped through, whereas the fundamentals data released on each minute is `None`, until the time in which the financial report's publishing date coincides. This ensure any algorithms being backtested do not have "future" data.

![aapl_reports](images/get_fundamentals.png "AAPL Reports")

### Data Dictionary

Below is the annotated model definitions and DBeaver data dictionary for the postgres database.

* All tables are owned by user `stockdata`.
* Column descriptions on commented inline.

```python
class Asset(Base):
    __tablename__ = 'asset'
    id = Column(Integer, primary_key=True)
    name = Column(String)                               # name of the asset / corporation
    symbol = Column(String)                             # unique identifier and ticker
    asset_type = Column(String)                         # type, one of stock / forex
    
    # constriants
    asset_uniq = UniqueConstraint('symbol', name='asset_name_uniq')


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

# Note:  Candlestick1H and Candlestick1D have identical data model as Candlestick1M


class FinancialReport(Base):
    __tablename__ = 'financial_report'
    id = Column(Integer, primary_key=True)
    asset_id = Column(Integer, ForeignKey('asset.id'))
    simfin_id = Column(String)                          # SimFin uniq report id
    fiscal_period = Column(String)                      # Fiscal Period, one of [Q1, Q2, Q3, Q4]
    fiscal_year = Column(Integer)                       # Fiscal Year
    report_date = Column(Date)                          # Report Date
    publish_date = Column(Date)                         # Published Date
    restated_date = Column(Date)                        # Restated Date (i.e. revision)
    source = Column(String)                             # Source document URI

    # constriants
    simfin_id_uniq = UniqueConstraint('simfin_id', name='simfin_id_uniq')

    # relationships
    asset = relationship("Asset", back_populates="financial_reports")
    profit_loss = relationship("ProfitLossReportData", back_populates="financial_report")
    balance_sheet = relationship("BalanceSheetReportData", back_populates="financial_report")
    cash_flow = relationship("CashFlowReportData", back_populates="financial_report")
    derived_data = relationship("DerivedReportData", back_populates="financial_report")


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


class BalanceSheetReportData(Base):
    __tablename__ = 'balance_sheet_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))
    
    cash_equivalents_st_investments = Column(Float)     # "Cash, Cash Equivalents & Short Term Investments"
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


class CashFlowReportData(Base):
    __tablename__ = 'cash_flow_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))

    net_income = Column(Float)                          # "Net Income\/Starting Line"
    depreciation_amortization = Column(Float)           # "Depreciation & Amortization"
    non_cash_items = Column(Float)                      # "Non-Cash Items"
    change_working_capital = Column(Float)              # "Change in Working Capital"
    net_cash_from_operating = Column(Float)             # "Net Cash from Operating Activities"
    change_in_fixed_assets = Column(Float)              # "Change in Fixed Assets & Intangibles"
    acquisition_fixed_assets = Column(Float)            # "Acquisition of Fixed Assets & Intangibles"
    net_change_lt_investment = Column(Float)            # "Net Change in Long Term Investment"
    decrease_lt_investment = Column(Float)              # "Decrease in Long Term Investment"
    increase_lt_investment = Column(Float)              # "Increase in Long Term Investment"
    net_cash_acquisitions = Column(Float)               # "Net Cash from Acquisitions & Divestitures"
    other_investing_activities = Column(Float)          # "Other Investing Activities"
    net_cash_investing_activies = Column(Float)         # "Net Cash from Investing Activities"
    dividents_paid = Column(Float)                      # "Dividends Paid"
    cash_from_debt = Column(Float)                      # "Cash from (Repayment of) Debt"
    cash_from_dt_debt_net = Column(Float)               # "Cash from (Repayment of) Short Term Debt Net"
    cash_from_equity = Column(Float)                    # "Cash from (Repurchase of) Equity"
    increase_capital_stock = Column(Float)              # "Increase in Capital Stock"
    decrease_capital_stock = Column(Float)              # "Decrease in Capital Stock"
    other_financing_activities = Column(Float)          # "Other Financing Activities"
    net_cash_financing_activities = Column(Float)       # "Net Cash from Financing Activities"
    net_cash_before_op_forex = Column(Float)            # "Net Cash Before Disc. Operations and FX"
    net_cash_before_fx = Column(Float)                  # "Net Cash Before FX"
    net_cash_in_cash = Column(Float)                    # "Net Change in Cash"
    financial_report = relationship("FinancialReport", back_populates="cash_flow")


class DerivedReportData(Base):
    __tablename__ = 'derived_report_data'
    id = Column(Integer, primary_key=True)
    financial_report_id = Column(Integer, ForeignKey('financial_report.id'))

    ebitda = Column(Float)                              # "EBITDA"
    total_debt = Column(Float)                          # "Total Debt"
    free_cash_flow = Column(Float)                      # "Free Cash Flow"
    gross_profit_margin = Column(Float)                 # "Gross Profit Margin"
    operating_margin = Column(Float)                    # "Operating Margin"
    net_profit_marge = Column(Float)                    # "Net Profit Margin"
    return_on_equity = Column(Float)                    # "Return on Equity"
    return_on_assets = Column(Float)                    # "Return on Assets"
    free_cash_flow_net = Column(Float)                  # "Free Cash Flow to Net Income"
    current_ratio = Column(Float)                       # "Current Ratio"
    liabilities_equity_ratio = Column(Float)            # "Liabilities to Equity Ratio"
    debt_ratio = Column(Float)                          # "Debt Ratio"
    earnings_per_share_basic = Column(Float)            # "Earnings Per Share Basic"
    earnings_per_share_diluted = Column(Float)          # "Earnings Per Share Diluted"
    sales_per_share = Column(Float)                     # "Sales Per Share"
    equity_per_share = Column(Float)                    # "Equity Per Share"
    free_cash_flow_per_share = Column(Float)            # "Free Cash Flow Per Share"
    dividends_per_share = Column(Float)                 # "Dividends Per Share"
    pietroski_f_score = Column(Float)                   # "Pietroski F-Score"
    financial_report = relationship("FinancialReport", back_populates="derived_data")
```

![data_dict](images/data_dictionary.png "Data Dictionary")