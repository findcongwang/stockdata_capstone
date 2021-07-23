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

### Data Dictionary / DDL

These are the DDL from SQLAlchemy's model creation.

```
CREATE TABLE public.asset (
	id serial NOT NULL,
	"name" varchar NULL,
	symbol varchar NULL,
	asset_type varchar NULL,
	CONSTRAINT asset_name_uniq UNIQUE (name),
	CONSTRAINT asset_pkey PRIMARY KEY (id)
);

CREATE TABLE public.candlestick_1d (
	asset_id int4 NOT NULL,
	"timestamp" timestamp NOT NULL,
	"open" float8 NOT NULL,
	high float8 NOT NULL,
	low float8 NOT NULL,
	"close" float8 NOT NULL,
	volume int4 NOT NULL,
	CONSTRAINT candlestick_1d_pkey PRIMARY KEY (asset_id, "timestamp"),
	CONSTRAINT candlestick_1d_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES asset(id)
);

CREATE TABLE public.candlestick_1h (
	asset_id int4 NOT NULL,
	"timestamp" timestamp NOT NULL,
	"open" float8 NOT NULL,
	high float8 NOT NULL,
	low float8 NOT NULL,
	"close" float8 NOT NULL,
	volume int4 NOT NULL,
	CONSTRAINT candlestick_1h_pkey PRIMARY KEY (asset_id, "timestamp"),
	CONSTRAINT candlestick_1h_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES asset(id)
);

CREATE TABLE public.candlestick_1m (
	asset_id int4 NOT NULL,
	"timestamp" timestamp NOT NULL,
	"open" float8 NOT NULL,
	high float8 NOT NULL,
	low float8 NOT NULL,
	"close" float8 NOT NULL,
	volume int4 NOT NULL,
	CONSTRAINT candlestick_1m_pkey PRIMARY KEY (asset_id, "timestamp"),
	CONSTRAINT candlestick_1m_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES asset(id)
);

CREATE TABLE public.financial_report (
	id serial NOT NULL,
	asset_id int4 NULL,
	simfin_id varchar NULL,
	fiscal_period varchar NULL,
	fiscal_year int4 NULL,
	report_date date NULL,
	publish_date date NULL,
	restated_date date NULL,
	"source" varchar NULL,
	CONSTRAINT financial_report_pkey PRIMARY KEY (id),
	CONSTRAINT financial_report_asset_id_fkey FOREIGN KEY (asset_id) REFERENCES asset(id)
);

CREATE TABLE public.profit_loss_report_data (
	id serial NOT NULL,
	financial_report_id int4 NULL,
	revenue float8 NULL,
	cost_revenue float8 NULL,
	gross_profit float8 NULL,
	operating_expenses float8 NULL,
	operating_income_loss float8 NULL,
	non_operating_income_loss float8 NULL,
	other_non_operating_income_loss float8 NULL,
	pretax_income_adj float8 NULL,
	pretax_income float8 NULL,
	income_tax_expense_net float8 NULL,
	net_income float8 NULL,
	net_income_common float8 NULL,
	CONSTRAINT profit_loss_report_data_pkey PRIMARY KEY (id),
	CONSTRAINT profit_loss_report_data_financial_report_id_fkey FOREIGN KEY (financial_report_id) REFERENCES financial_report(id)
);

CREATE TABLE public.balance_sheet_report_data (
	id serial NOT NULL,
	financial_report_id int4 NULL,
	cash_equivalents_st_investments float8 NULL,
	cash_equivalents float8 NULL,
	st_investments float8 NULL,
	accounts_receivable float8 NULL,
	accounts_receivable_net float8 NULL,
	inventories float8 NULL,
	other_st_assets float8 NULL,
	misc_st_assets float8 NULL,
	total_current_assets float8 NULL,
	property_equipment_net float8 NULL,
	lt_investments float8 NULL,
	other_lt_assets float8 NULL,
	misc_lt_assets float8 NULL,
	toal_noncurrent_assets float8 NULL,
	total_assets float8 NULL,
	payables_accurals float8 NULL,
	accounts_payable float8 NULL,
	st_debt float8 NULL,
	other_st_liabilities float8 NULL,
	deferred_revenue float8 NULL,
	misc_st_liabilities float8 NULL,
	totoal_current_liabilities float8 NULL,
	lt_debt float8 NULL,
	other_lt_liabilities float8 NULL,
	misc_lt_liabilities float8 NULL,
	total_noncurrent_liabilities float8 NULL,
	total_liabilities float8 NULL,
	share_add_capital float8 NULL,
	retained_earnings float8 NULL,
	other_equity float8 NULL,
	equity_before_minority_interest float8 NULL,
	total_equity float8 NULL,
	total_liabilities_equity float8 NULL,
	CONSTRAINT balance_sheet_report_data_pkey PRIMARY KEY (id),
	CONSTRAINT balance_sheet_report_data_financial_report_id_fkey FOREIGN KEY (financial_report_id) REFERENCES financial_report(id)
);

CREATE TABLE public.cash_flow_report_data (
	id serial NOT NULL,
	financial_report_id int4 NULL,
	net_income float8 NULL,
	depreciation_amortization float8 NULL,
	non_cash_items float8 NULL,
	change_working_capital float8 NULL,
	net_cash_from_operating float8 NULL,
	change_in_fixed_assets float8 NULL,
	acquisition_fixed_assets float8 NULL,
	net_change_lt_investment float8 NULL,
	decrease_lt_investment float8 NULL,
	increase_lt_investment float8 NULL,
	net_cash_acquisitions float8 NULL,
	other_investing_activities float8 NULL,
	net_cash_investing_activies float8 NULL,
	dividents_paid float8 NULL,
	cash_from_debt float8 NULL,
	cash_from_dt_debt_net float8 NULL,
	cash_from_equity float8 NULL,
	increase_capital_stock float8 NULL,
	decrease_capital_stock float8 NULL,
	other_financing_activities float8 NULL,
	net_cash_financing_activities float8 NULL,
	net_cash_before_op_forex float8 NULL,
	net_cash_before_fx float8 NULL,
	net_cash_in_cash float8 NULL,
	CONSTRAINT cash_flow_report_data_pkey PRIMARY KEY (id),
	CONSTRAINT cash_flow_report_data_financial_report_id_fkey FOREIGN KEY (financial_report_id) REFERENCES financial_report(id)
);

CREATE TABLE public.derived_report_data (
	id serial NOT NULL,
	financial_report_id int4 NULL,
	ebitda float8 NULL,
	total_debt float8 NULL,
	free_cash_flow float8 NULL,
	gross_profit_margin float8 NULL,
	operating_margin float8 NULL,
	net_profit_marge float8 NULL,
	return_on_equity float8 NULL,
	return_on_assets float8 NULL,
	free_cash_flow_net float8 NULL,
	current_ratio float8 NULL,
	liabilities_equity_ratio float8 NULL,
	debt_ratio float8 NULL,
	earnings_per_share_basic float8 NULL,
	earnings_per_share_diluted float8 NULL,
	sales_per_share float8 NULL,
	equity_per_share float8 NULL,
	free_cash_flow_per_share float8 NULL,
	dividends_per_share float8 NULL,
	pietroski_f_score float8 NULL,
	CONSTRAINT derived_report_data_pkey PRIMARY KEY (id),
	CONSTRAINT derived_report_data_financial_report_id_fkey FOREIGN KEY (financial_report_id) REFERENCES financial_report(id)
);

```