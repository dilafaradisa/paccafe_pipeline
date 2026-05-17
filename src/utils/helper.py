import os
import pandas as pd
import sqlalchemy
import gspread
from dotenv import load_dotenv
from sqlalchemy import create_engine
from datetime import datetime
from minio import Minio
from io import BytesIO
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

SRC_DB_HOST=os.getenv("SRC_POSTGRES_HOST")
SRC_DB_USER=os.getenv("SRC_POSTGRES_USER")
SRC_DB_PASSWORD=os.getenv("SRC_POSTGRES_PASSWORD")
SRC_DB_PORT=os.getenv("SRC_POSTGRES_PORT")
SRC_DB_NAME=os.getenv("SRC_POSTGRES_DB") 

STG_DB_HOST=os.getenv("STG_POSTGRES_HOST")
STG_DB_USER=os.getenv("STG_POSTGRES_USER")
STG_DB_PASSWORD=os.getenv("STG_POSTGRES_PASSWORD")
STG_DB_PORT=os.getenv("STG_POSTGRES_PORT")
STG_DB_NAME=os.getenv("STG_POSTGRES_DB")

DWH_DB_HOST=os.getenv("DWH_POSTGRES_HOST")
DWH_DB_USER=os.getenv("DWH_POSTGRES_USER")
DWH_DB_PASSWORD=os.getenv("DWH_POSTGRES_PASSWORD")
DWH_DB_PORT=os.getenv("DWH_POSTGRES_PORT")
DWH_DB_NAME=os.getenv("DWH_POSTGRES_DB")

LOG_DB_HOST=os.getenv("LOG_POSTGRES_HOST")
LOG_DB_USER=os.getenv("LOG_POSTGRES_USER")
LOG_DB_PASSWORD=os.getenv("LOG_POSTGRES_PASSWORD")
LOG_DB_PORT=os.getenv("LOG_POSTGRES_PORT")
LOG_DB_NAME=os.getenv("LOG_POSTGRES_DB")

CRED_PATH = os.getenv("CRED_PATH")
KEY_SPREADSHEET = os.getenv("SPREADSHEET_KEY")
MODEL_PATH = os.getenv("MODEL_PATH")

ACCESS_KEY_MINIO = os.getenv("MINIO_ROOT_USER")
SECRET_KEY_MINIO = os.getenv("MINIO_ROOT_PASSWORD")

def read_sql(table_name):
    # open .sql
    with open(f"{MODEL_PATH}{table_name}.sql", 'r') as file:
        content = file.read()

    # return query text
    return content

def etl_log(log_msg: dict):
    try:
        # create connection to log database
        conn = create_engine(f"postgresql://{LOG_DB_USER}:{LOG_DB_PASSWORD}@{LOG_DB_HOST}:{LOG_DB_PORT}/{LOG_DB_NAME}")

        # convert dictionary to dataframe
        df_log = pd.DataFrame([log_msg])

        # insert log tp db
        df_log.to_sql(name = "etl_log", 
                        con = conn,
                        if_exists = "append",
                        index = False)
        
    except Exception as e:
        print("Can't save your log message. Cause: ", str(e))

def read_etl_log(filter_params: dict):

    try:
        # create connection to database
        conn = create_engine(f"postgresql://{LOG_DB_USER}:{LOG_DB_PASSWORD}@{LOG_DB_HOST}:{LOG_DB_PORT}/{LOG_DB_NAME}")

        # To help with the incremental process, get the etl_date from the relevant process
        """
        SELECT MAX(etl_date)
        FROM etl_log "
        WHERE
            step = %s and
            component = %s and
            table_name ilike %s and
            status = %s 
        """
        query = sqlalchemy.text(read_sql("log"))

        # execute the query with pd.read_sql
        df = pd.read_sql(sql=query, con=conn, params=(filter_params,))

        # return extracted data
        return df
    
    except Exception as e:
        print("Can't execute your query. Cause: ", str(e))


def handle_error(data, bucket_name: str, table_name: str):
    
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Initialize MinIO client
    client = Minio(
        endpoint='localhost:9000',
        access_key=ACCESS_KEY_MINIO,
        secret_key=SECRET_KEY_MINIO,
        secure=False
    ) 
    
    # Create a bucket if it does not exist
    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)
        
    # Convert Dataframe tp CSV and then to Bytes
    csv_bytes = data.to_csv().encode('utf-8')
    csv_buffer = BytesIO(csv_bytes)
    
    # Upload the CSV file to the bucket
    client.put_object(
        bucket_name=bucket_name,
        object_name=f"{table_name}_{current_date}.csv",
        data=csv_buffer,
        length=len(csv_bytes),
        content_type='application/csv'
    )
    
    # List object in the bucket
    objects = client.list_objects(bucket_name, recursive=True)
    for obj in objects:
        print(obj.object_name)


def extract_target(table_name: str):
    conn = create_engine(f"postgresql://{DWH_DB_USER}:{DWH_DB_PASSWORD}@{DWH_DB_HOST}:{DWH_DB_PORT}/{DWH_DB_NAME}")
    
    # select all from the table
    query = f"SELECT * FROM {table_name}"
    df = pd.read_sql(query, conn)
    
    return df


