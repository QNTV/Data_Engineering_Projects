import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

from prefect_dbt.cloud import DbtCloudJob
from prefect_dbt.cloud.jobs import run_dbt_cloud_job

LOCATION = 'europe-west3'
PROJECT = 'dtc-project'
DATASET = 'ga_data'
GA_TABLE_RAW = 'ga_data'
GA_TABLE_PROCESSED = 'ga_data_processed'
GA_PARQUET_FILENAME = 'ga_data.parquet'
GA_STORAGE = 'gs//ga_storage_dtc-project'
gcp_credentials_block = GcpCredentials.load("dtc-de-gcp")

@task(retries = 1, log_prints = True)
