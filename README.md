# StockEvents (Udacity Capstone)

This project collects ticker and fundamental data, and offers a framework to compute various signal events for persistence and analysis. For example, a LSTM neural network to detect trade patterns.

StockEvents is a custom Udacity Data Engineering Nanodegree capstone project. As such, it has corresponding requirements:

### Project Scope
* Ticker data is fetched via Questrade and TradingView, whereas fundamentals data is fetched from SimFin. Hourly data is fetched from an universe of stock symbols and will exceed 1 million records.
* The end use cases for the organized data is for quantamental (quantitive + fundamental) analysis. This project builds the source of truth tables for the core data, as well as extended dimensions tables from technical indicators.

### Data Cleanup
* Finanical data records are missing on non-trading hours (i.e. after-hours, weekends, holidays), which is expected. Both sources are adjusted for dividends and splits so there is no processing required on that front.
* === TODO: datacleaning

### Data Model
* === TODO: Data schema
* === TODO: transformation steps

### ETL Pipeline
* === TODO: folder structure with etl.py and /data directory
* === TODO: list our data integrity checks and pytest coverage, test summary

### Tech Stack Rationale
* What's the goal? 
* What queries will you want to run? 
* How would Spark or Airflow be incorporated?
* Why did you choose the model you chose?
* Clearly state the rationale for the choice of tools and technologies for the project.
* Document the steps of the process.
* Propose how often the data should be updated and why.

### Notes on Scaled Scenarios

```    
Include a description of how you would approach the problem differently under the following scenarios:
    If the data was increased by 100x.
    If the pipelines were run on a daily basis by 7am.
    If the database needed to be accessed by 100+ people.
```
