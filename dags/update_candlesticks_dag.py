from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from stockdata.utils.alphavantage_loader import load_candlesticks
from stockdata.models import session, Asset


def run_load_candlesticks(ticker, *args, **kwargs):
    load_candlesticks(ticker)


dag = DAG(
    start_date=datetime.now(),
    dag_id="update_candlesticks",
    max_active_runs=1,
    schedule_interval="0 0 * * *")

assets = session.query(Asset).all()
for asset in assets:
    task = PythonOperator(
        task_id="update_candlesticks_{}".format(asset.symbol),
        python_callable=run_load_candlesticks,
        retries=2,
        retry_delay=timedelta(seconds=1),
        op_args=[asset.symbol],
        dag=dag,
    )
