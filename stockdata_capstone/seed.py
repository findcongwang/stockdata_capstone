import os
from dotenv import load_dotenv

from sqlalchemy import create_engine


DB_CONNECTION = os.environ.get("DB_CONNECTION")
engine = create_engine(DB_CONNECTION, echo = True)

asset_seed_query = """
INSERT INTO asset ("name", "symbol", "asset_type") VALUES
    ('APPLE INC.', 'AAPL', 'stock'),
    ('TESLA INC.', 'TSLA', 'stock'),
    ('MICROSOFT CORP.', 'MSFT', 'stock'),
    ('AMAZON.COM INC.', 'AMZN', 'stock')
ON CONFLICT (name) DO NOTHING;
"""


def main():
    load_dotenv()
    with engine.connect() as conn:
        conn.execute(asset_seed_query)


if __name__ == "__main__":
    main()
