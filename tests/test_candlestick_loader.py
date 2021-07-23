import os
import pytest
import pendulum

from datetime import timedelta
from dotenv import load_dotenv
from stockdata.models import (
    engine, session, Asset, 
    Candlestick1M, Candlestick1H, Candlestick1D
)


"""
Tests to be ran after the ETL process is triggered manually.
"""

load_dotenv()
BACK_POPULATE_MONTHS = int(os.environ.get("BACK_POPULATE_MONTHS"))


def test_candlestick_1m_count():
    last_candle = session.query(Candlestick1M).order_by(
        Candlestick1M.timestamp.desc()).first()
    first_candle = session.query(Candlestick1M).order_by(
        Candlestick1M.timestamp.asc()).first()

    end_time = pendulum.now().naive()
    start_time = end_time.add(months=-BACK_POPULATE_MONTHS)
    assert last_candle.timestamp + timedelta(hours=48) > end_time
    assert first_candle.timestamp + timedelta(hours=48) > start_time
    
    
def test_candlestick_1h_count():
    last_candle = session.query(Candlestick1H).order_by(
        Candlestick1H.timestamp.desc()).first()
    first_candle = session.query(Candlestick1H).order_by(
        Candlestick1H.timestamp.asc()).first()

    end_time = pendulum.now().naive()
    start_time = end_time.add(months=-BACK_POPULATE_MONTHS)
    assert last_candle.timestamp + timedelta(hours=48) > end_time
    assert first_candle.timestamp + timedelta(hours=48) > start_time
    
    
def test_candlestick_1d_count():
    last_candle = session.query(Candlestick1D).order_by(
        Candlestick1D.timestamp.desc()).first()
    first_candle = session.query(Candlestick1D).order_by(
        Candlestick1D.timestamp.asc()).first()

    end_time = pendulum.now().naive()
    start_time = end_time.add(months=-BACK_POPULATE_MONTHS)
    assert last_candle.timestamp + timedelta(hours=48) > end_time
    assert first_candle.timestamp + timedelta(hours=48) > start_time
