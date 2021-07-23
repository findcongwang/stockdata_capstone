from airflow.models import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from collections import defaultdict
from stockdata.utils.simfin_loader import load_fundamentals, STATEMENT_CLS_LOOKUP
from stockdata.models import session, Asset


def run_load_fundamentals(ticker, statement_type, *args, **kwargs):
    load_fundamentals(ticker, statement_type)


dag = DAG(
    start_date=datetime.now(),
    dag_id="update_fundamentals",
    max_active_runs=1,
    schedule_interval="0 0 1 * *")

assets = session.query(Asset).all()
task_map = defaultdict(list)
for statement_type in STATEMENT_CLS_LOOKUP:
    for asset in assets:
        task = PythonOperator(
            task_id="update_fundamentals_{}_{}".format(asset.symbol, statement_type),
            python_callable=run_load_fundamentals,
            retries=2,
            retry_delay=timedelta(seconds=1),
            op_args=[asset.symbol, statement_type],
            dag=dag,
        )
        if len(task_map[statement_type]) > 0:
            task_map[statement_type][-1] >> task
        task_map[statement_type].append(task)
