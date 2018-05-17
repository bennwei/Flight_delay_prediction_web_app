import sys, os, re

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta
import iso8601

project_home = os.environ["PROJECT_HOME"]

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': iso8601.parse_date("2016-12-01"),
  'email': ['russell.jurney@gmail.com'],
  'email_on_failure': True,
  'email_on_retry': True,
  'retries': 3,
  'retry_delay': timedelta(minutes=5),
}

# Timedelta 1 is 'run daily'
dag = DAG(
  'agile_data_science_airflow_test',
  default_args=default_args,
  schedule_interval=timedelta(1)
)

# Run a simple PySpark Script
pyspark_local_task_one = BashOperator(
  task_id = "pyspark_local_task_one",
  bash_command = """spark-submit \
  --master {{ params.master }}
  {{ params.base_path }}/{{ params.filename }} {{ ts }} {{ params.base_path }}""",
  params = {
    "master": "local[8]",
    "filename": "ch02/pyspark_task_one.py",
    "base_path": "{}/".format(project_home)
  },
  dag=dag
)

# Run another simple PySpark Script that depends on the previous one
pyspark_local_task_two = BashOperator(
  task_id = "pyspark_local_task_two",
  bash_command = """spark-submit \
  --master {{ params.master }}
  {{ params.base_path }}/{{ params.filename }} {{ ts }} {{ params.base_path }}""",
  params = {
    "master": "local[8]",
    "filename": "ch02/pyspark_task_two.py",
    "base_path": "{}/".format(project_home)
  },
  dag=dag
)

# Add the dependency from the second to the first task
pyspark_local_task_two.set_upstream(pyspark_local_task_one)
