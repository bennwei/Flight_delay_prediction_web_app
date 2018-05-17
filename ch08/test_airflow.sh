#!/bin/bash

# Compute today's date:
export ISO_DATE=`date "+%Y-%m-%d"`

# List DAGs
airflow list_dags

# List tasks in each DAG
airflow list_tasks agile_data_science_batch_prediction_model_training
airflow list_tasks agile_data_science_batch_predictions_daily

# Test each task in each DAG
airflow test agile_data_science_batch_prediction_model_training pyspark_extract_features $ISO_DATE
airflow test agile_data_science_batch_prediction_model_training pyspark_train_classifier_model $ISO_DATE

airflow test agile_data_science_batch_predictions_daily pyspark_fetch_prediction_requests $ISO_DATE
airflow test agile_data_science_batch_predictions_daily pyspark_make_predictions $ISO_DATE
airflow test agile_data_science_batch_predictions_daily pyspark_load_prediction_results $ISO_DATE

# Test the training and persistence of the models
airflow backfill -s $ISO_DATE -e $ISO_DATE agile_data_science_batch_prediction_model_training

# Test the daily operation of the model
airflow backfill -s $ISO_DATE -e $ISO_DATE agile_data_science_batch_predictions_daily
