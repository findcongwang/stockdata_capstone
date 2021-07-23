import os
import requests
import numpy as np
import pandas as pd

from datetime import datetime, timedelta
from dotenv import load_dotenv

from stockdata.models import (
    engine, session, Asset, 
    Candlestick1M, Candlestick1H, Candlestick1D
)

RESAMPLE_PARAMS = {
    "open": "first", "high": np.max, "low": np.min, "close": "last", 
    "volume": np.sum,
}

CANDLESTICK_INSERT_QUERY_BASE = """
INSERT INTO {} 
    ("timestamp", "open", "high", "low", "close", "volume", "asset_id") 
VALUES {}
ON CONFLICT (asset_id, timestamp) DO NOTHING;
"""


def sanitize_tuple(tup, asset_id):
    return "{}".format(
        (tup[0].isoformat(),) + tup[1:] + (asset_id,))


def load_candlesticks(ticker, max_slices=12):
    """
    Loads 1M candlestick data from AlphaVantage and resamples into 1h and 1d.
    - resampling from 1m -> 1h is closed-right
    - resampling from 1h -> 1d is default
    - checks now() and last_candle for the query "slice" as "year2monthX"
    """
    ALPHAVANTAGE_API = os.environ.get('ALPHAVANTAGE_API')
    ALPHAVANTAGE_API_KEY = os.environ.get('ALPHAVANTAGE_API_KEY')

    # get asset by ticker
    asset = session.query(Asset).filter(Asset.symbol == ticker).first()
    if asset is None:
        return

    last_candle = session.query(Candlestick1M).order_by(
        Candlestick1M.timestamp.desc()).first()

    # pull all slices if no data yet
    if last_candle is None:
        slices = ["year1month{}".format(i+1) for i in range(max_slices)]

    # otherwise calc the slice to fetch from timestamp
    else:
        slices = []
        end_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        for i in range(max_slices):
            slice_end_date = end_date - timedelta(days=30*(i+1))
            if last_candle.timestamp < slice_end_date:
                slices.append("year1month{}".format(i+1))


    for query_slice in slices:
        print("fetching for slice {}...".format(query_slice))
        query = "{}/query?function={}&symbol={}&interval={}&slice={}&apikey={}".format(
            ALPHAVANTAGE_API,
            "TIME_SERIES_INTRADAY_EXTENDED",
            ticker,
            "1min",
            query_slice,
            ALPHAVANTAGE_API_KEY,
        )
        candles_1m = pd.read_csv(query)
        candles_1m = candles_1m.set_index('time')
        candles_1m.index = pd.to_datetime(candles_1m.index)

        # upsert the 1m records
        row_tuples = [
            sanitize_tuple(tup, asset.id) for tup in candles_1m.itertuples(index=True, name=None)]
        candlestick_insert_query = CANDLESTICK_INSERT_QUERY_BASE.format(
            Candlestick1M.__tablename__, ",\n".join(row_tuples)
        )
        with engine.connect() as conn:
            conn.execute(candlestick_insert_query)

        # resample and upsert 1h records
        candles_1h = candles_1m.resample('1h', closed='right').agg(RESAMPLE_PARAMS).dropna()
        row_tuples = [
            sanitize_tuple(tup, asset.id) for tup in candles_1h.itertuples(index=True, name=None)]
        candlestick_insert_query = CANDLESTICK_INSERT_QUERY_BASE.format(
            Candlestick1H.__tablename__, ",\n".join(row_tuples)
        )
        with engine.connect() as conn:
            conn.execute(candlestick_insert_query)

        # resample and upsert 1d records
        candles_1d = candles_1h.resample('1d').agg(RESAMPLE_PARAMS).dropna()
        row_tuples = [
            sanitize_tuple(tup, asset.id) for tup in candles_1d.itertuples(index=True, name=None)]
        candlestick_insert_query = CANDLESTICK_INSERT_QUERY_BASE.format(
            Candlestick1D.__tablename__, ",\n".join(row_tuples)
        )
        with engine.connect() as conn:
            conn.execute(candlestick_insert_query)


def main():
    load_dotenv()
    BACK_POPULATE_MONTHS = int(os.environ.get("BACK_POPULATE_MONTHS"))
    load_candlesticks("AAPL", max_slices=BACK_POPULATE_MONTHS)


if __name__ == "__main__":
    main()
