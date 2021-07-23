import os
import requests
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from dotenv import load_dotenv
from sqlalchemy import insert

from stockdata.models import (
    engine, session, Asset, 
    FinancialReport, ProfitLossReportData, BalanceSheetReportData,
    CashFlowReportData, DerivedReportData
)

STATEMENT_CLS_LOOKUP = {
    "pl": ProfitLossReportData,
    "bs": BalanceSheetReportData,
    "cf": CashFlowReportData,
    "derived": DerivedReportData,
}


def get_simfin_value(resp, key):
    try:
        key_idx = resp["columns"].index(key)
        return resp["data"][0][key_idx]
    except ValueError:
        return None


def get_orm_dict(resp, report_cls):
    lookup = report_cls.simfin_property_lookup()
    return { 
        key: get_simfin_value(resp, lookup[key])
        for key in lookup.keys()
    }


def load_fundamentals(ticker, statement_type):
    """
    Loads the corresponding statement_type for ticker from SimFin.
    - the common report fields are upserted
    - properties mappings are defined on the models
    """
    SIMFIN_API = os.environ.get('SIMFIN_API')
    SIMFIN_API_KEY = os.environ.get('SIMFIN_API_KEY')

    # get asset by ticker
    asset = session.query(Asset).filter(Asset.symbol == ticker).first()
    if asset is None:
        return

    # fetch data for each quarter of the prev and current year
    current_year = datetime.now().year
    for year in [current_year-1, current_year]:
        for period in ["q1", "q2", "q3", "q4"]:
            query_url = "{}/companies/statements?ticker={}&statement={}&period={}&fyear={}&api-key={}".format(
                SIMFIN_API,
                ticker,
                statement_type,
                period,
                year,
                SIMFIN_API_KEY,
            )
            resp = requests.get(query_url).json()[0]
            if not resp["found"]:
                continue

            # lookup the financial report by simfin_id, if None then insert
            simfin_id = get_simfin_value(resp, "SimFinId")
            fiscal_year = get_simfin_value(resp, "Fiscal Year")
            fiscal_period = get_simfin_value(resp, "Fiscal Period")
            financial_report = session.query(FinancialReport).filter(
                FinancialReport.simfin_id == str(simfin_id),
                FinancialReport.fiscal_year == fiscal_year,
                FinancialReport.fiscal_period == fiscal_period,
            ).first()            

            if financial_report is None:
                props = get_orm_dict(resp, FinancialReport)
                financial_report = FinancialReport(asset_id=asset.id, **props)
                session.add(financial_report)
                session.commit()
            
            # now insert the fetched report
            report_cls = STATEMENT_CLS_LOOKUP[statement_type]
            props = get_orm_dict(resp, report_cls)

            report_data = session.query(report_cls).filter(
                report_cls.financial_report_id == financial_report.id).first()
            
            if report_data is None:
                report_data = report_cls(financial_report_id=financial_report.id, **props)
                session.add(report_data)
                session.commit()


def main():
    load_dotenv()
    load_fundamentals("AAPL", "pl")
    load_fundamentals("AAPL", "bs")
    load_fundamentals("AAPL", "cf")
    load_fundamentals("AAPL", "derived")

if __name__ == "__main__":
    main()
