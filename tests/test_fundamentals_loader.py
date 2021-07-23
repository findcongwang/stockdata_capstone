import os
import pytest
import pendulum

from datetime import timedelta
from dotenv import load_dotenv

from stockdata.models import (
    engine, session, Asset, 
    FinancialReport, ProfitLossReportData, BalanceSheetReportData,
    CashFlowReportData, DerivedReportData
)

"""
Tests to be ran after the ETL process is triggered manually.
"""

load_dotenv()


def test_fundmental_report():
    for report_cls in [FinancialReport, ProfitLossReportData, BalanceSheetReportData,
    CashFlowReportData, DerivedReportData]:
        # since we pull the prev year, there should be at least 4 reports of each type
        count = session.query(report_cls).count()
        assert count >= 4