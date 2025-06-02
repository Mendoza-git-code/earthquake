from datetime import date, timedelta
import requests
import json
import pendulum

from airflow import DAG
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.cloud.transfers.local_to_gcs import LocalFilesystemToGCSOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
#from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.operators.python import PythonOperator


def http_extract_data(**kwargs):
    print(kwargs)
    start_date = kwargs['ds']
    start_date_nodash = kwargs['ds_nodash']
    end_date = (date.fromisoformat(start_date) + timedelta(days=1)).strftime("%Y-%m-%d")
    url = f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_date}&endtime={end_date}&minmagnitude=1'
    data_path = f"/tmp/earthquake_{start_date_nodash}.json"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()['features']

        with open(data_path, "w") as file:
            for item in data:
                file.write(json.dumps(item))
                file.write('\n')
    else:
        raise Exception(f"Failed to fetch data: {response.status_code}, {response.text}")

# Define the DAG and default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2025, 5, 1, tz="UTC"),
    'retries': 3,
}

with DAG(
    'earthquake',
    default_args=default_args,
    description='ETL pipeline for earthquake data to BigQuery',
    schedule='0 9 * * *',
    catchup=False,
) as dag:

    http_extract_data = PythonOperator(
        task_id='http_extract_data',
        python_callable=http_extract_data,
    )

    transform_data_spark = SSHOperator(
        task_id='transform_data_spark',
        ssh_conn_id='spark-service-local',
        command='export JAVA_HOME=/opt/java/openjdk; /opt/spark/bin/spark-submit /opt/spark-apps/test_script.py',
    )

    load_file_to_gcs = LocalFilesystemToGCSOperator(
        task_id = "load_file_to_gcs",
        src = "/tmp/earthquake_{{ ds_nodash }}.json",
        bucket = "starlingcontacts-data-dev",
        dst = "earthquake/{{ ds_nodash }}.json",
        gcp_conn_id="gcp-starlingcontacts-data-dev",
    )

    #load_transformed_file_to_gcs = LocalFilesystemToGCSOperator(
    #    task_id = "load_transformed_file_to_gcs",
    #    src = "/tmp/earthquake_transformed{{ ds_nodash }}.json",
    #    bucket = "starlingcontacts-data-dev",
    #    dst = "earthquake_transformed/{{ ds_nodash }}.json",
    #    gcp_conn_id="gcp-starlingcontacts-data-dev",
    #)

    load_gcs_to_bq = GCSToBigQueryOperator(
        task_id = "load_gcs_to_bq",
        bucket = "starlingcontacts-data-dev",
        source_objects=['earthquake/{{ ds_nodash }}.json'],
        destination_project_dataset_table = "staging_temp.earthquake_{{ ds_nodash }}",
        write_disposition = "WRITE_TRUNCATE",
        source_format = 'NEWLINE_DELIMITED_JSON',
        gcp_conn_id="gcp-starlingcontacts-data-dev",
    )

    bq_transform_event = BigQueryInsertJobOperator(
        task_id = "bq_transform_event",
        configuration={
            "query": {
                "destinationTable": {
                   "projectId": "starlingcontacts-data-dev",
                   "datasetId": "earthquake_model",
                   "tableId": "event_earthquake${{ ds_nodash }}"
                },
                "query": "{% include './sql/event_earthquake.sql' %}",
                "useLegacySql": False,
                "writeDisposition": "WRITE_TRUNCATE_DATA"
            }
        },
        gcp_conn_id="gcp-starlingcontacts-data-dev",
    )

    http_extract_data >> load_file_to_gcs >> load_gcs_to_bq >> bq_transform_event
    http_extract_data >> transform_data_spark #>> load_transformed_file_to_gcs
