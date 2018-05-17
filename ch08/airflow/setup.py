import sys, os, re

from airflow import DAG
from airflow.operators.bash_operator import BashOperator

from datetime import datetime, timedelta
import iso8601

PROJECT_HOME = os.environ["PROJECT_HOME"]

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': iso8601.parse_date("2016-12-01"),
  'email': ['ericliaowei@gmail.com'],
  'email_on_failure': True,
  'email_on_retry': True,
  'retries': 3,
  'retry_delay': timedelta(minutes=5),
}

training_dag = DAG(
  'agile_data_science_batch_prediction_model_training',
  default_args=default_args
)

# We use the same two commands for all our PySpark tasks
pyspark_bash_command = """
spark-submit --master {{ params.master }} \
  {{ params.base_path }}/{{ params.filename }} \
  {{ params.base_path }}
"""
pyspark_date_bash_command = """
spark-submit --master {{ params.master }} \
  {{ params.base_path }}/{{ params.filename }} \
  {{ ts }} {{ params.base_path }}
"""


# Gather the training data for our classifier
extract_features_operator = BashOperator(
  task_id = "pyspark_extract_features",
  bash_command = pyspark_bash_command,
  params = {
    "master": "local[8]",
    "filename": "ch08/extract_features.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=training_dag
)

# Train and persist the classifier model
train_classifier_model_operator = BashOperator(
  task_id = "pyspark_train_classifier_model",
  bash_command = pyspark_bash_command,
  params = {
    "master": "local[8]",
    "filename": "ch08/train_spark_mllib_model.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=training_dag
)

# The model training depends on the feature extraction
train_classifier_model_operator.set_upstream(extract_features_operator)

daily_prediction_dag = DAG(
  'agile_data_science_batch_predictions_daily',
  default_args=default_args,
  schedule_interval=timedelta(1)
)

# Fetch prediction requests from MongoDB
fetch_prediction_requests_operator = BashOperator(
  task_id = "pyspark_fetch_prediction_requests",
  bash_command = pyspark_date_bash_command,
  params = {
    "master": "local[8]",
    "filename": "ch08/fetch_prediction_requests.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=daily_prediction_dag
)

# Make the actual predictions for today
make_predictions_operator = BashOperator(
  task_id = "pyspark_make_predictions",
  bash_command = pyspark_date_bash_command,
  params = {
    "master": "local[8]",
    "filename": "ch08/make_predictions.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=daily_prediction_dag
)

# Load today's predictions to Mongo
load_prediction_results_operator = BashOperator(
  task_id = "pyspark_load_prediction_results",
  bash_command = pyspark_date_bash_command,
  params = {
    "master": "local[8]",
    "filename": "ch08/load_prediction_results.py",
    "base_path": "{}/".format(PROJECT_HOME)
  },
  dag=daily_prediction_dag
)

# Set downstream dependencies for daily_prediction_dag
fetch_prediction_requests_operator.set_downstream(make_predictions_operator)
make_predictions_operator.set_downstream(load_prediction_results_operator)
