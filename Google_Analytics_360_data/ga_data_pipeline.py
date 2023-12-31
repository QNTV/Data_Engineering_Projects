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
def read_from_bp() -> pd.DataFrame:
    """Task to load dta from BQ table to pandas dataframe
        Data gathered by SQL query
        Data load to cloud storage in parquet format.
        
        Args:
            None.
            
        Return:
            Dataframe.
    """
    query = """
                    SELECT
                        CAST(date AS DATE FORMAT 'YYYYMMDD) AS date,
                        CAST(fullVisitorId AS STRING) AS fullVisitorId,
                        totals.transactions AS transactions,
                        device.browser AS browser,
                        totals.timeOnSite AS timeOnSite,
                        channelGrouping AS channelGrouping,
                        geoNetwork.country AS country,
                        totals.newVisits AS newVisits,
                        totals.visits AS visits,
                    FROM
                        'bigquery-public-data.google_analytics_sample.ga_session_*'
            """
    return pd.read_gbq(query, project_id= PROJECT)


@task(retries = 1, log_prints = True)
def write_to_gcs(df: pd.DataFrame) -> None:
    """"
        Upload local parquet file to GCS
        
        Args:
            Dataframe and path
            
        Returns:
            None.
    """
    
    gcs_block = GcsBucket.load("dtc-de-gcs")
    return gcs_block.upload_from_dataframe(df = df, to_path= GA_PARQUET_FILENAME, serialization_format = 'parquet')

    
@task(retries = 1, log_prints = True)
def extract_from_gcs(path) -> pd.DataFrame:
    """
        Download trip data from GCS

        Args:
            Dataframe and path
            
        Returns:
            None.        
        
    """
    print(path)
    df = pd.read_parquet(path)
    return df


@task(retries = 1, log_prints = True)
def write_to_bq(df: pd.DataFrame) -> None:
    """
        Write DataFrame to BigQuery
        
        Args:
            DataFrame.
            
        Returns:
            None.
    """
    
    df['date'] = pd.to_datetime(df.date, format='%Y-%m-%dT%H:%M:%S.%f', errors='ignore')
    df['date'] = df.date.dt.date
    df['fullVisitorId'] = df.fullVisitorId.astype(str)
    
    df.to_gbq(
        destination_table = f"{DATASET}.{GA_TABLE_RAW}",
        project_id = PROJECT,
        credential = gcp_credentials_block.get_credentials_from_service_account,
        cunksize = 500_000,
        if_exists = "replace",
    )            
    return True


@flow(log_prints = True)
def ga_data_flow():
    """General function of DAG orchestrates task
        Args:
            None.
            
        Returns:
            None.
    """
    
    df = read_from_bp()
    path = write_to_gcs(df)
    patch = f'GA_STORAGE}/{patch}'
    df = extract_from_gcs(path)
    write_to_bq(df)
    
    #Run dbt job which processing raw date to mart data
    result = run_dbt_cloud_job(
        dbt_cloud_job = DbtCloudJob.load("dtc-de-dbt"),
        targeted_retries = 3
    )
    return result


if __name__ == "__main__":
    ga_data_flow()
    