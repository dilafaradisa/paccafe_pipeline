import os
import pandas as pd
import sqlalchemy
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pangres import upsert
from datetime import datetime
from src.utils.helper import etl_log, handle_error

load_dotenv()

STG_DB_HOST=os.getenv("STG_POSTGRES_HOST")
STG_DB_USER=os.getenv("STG_POSTGRES_USER")
STG_DB_PASSWORD=os.getenv("STG_POSTGRES_PASSWORD")
STG_DB_PORT=os.getenv("STG_POSTGRES_PORT")
STG_DB_NAME=os.getenv("STG_POSTGRES_DB")

def load_to_staging(data, schema: str, table_name: str, idx_name: str):
    
    try:
        conn = create_engine(f"postgresql://{STG_DB_USER}:{STG_DB_PASSWORD}@{STG_DB_HOST}:{STG_DB_PORT}/{STG_DB_NAME}")
        
        # Set data index for Primary Key
        data = data.set_index(idx_name)
        
        # Apply upsert (update existing records, insert new records)
        upsert(
            con=conn,
            df=data,
            table_name=table_name,
            schema=schema,
            if_row_exists='update'
        )
        print(f"Data loaded to staging for table: {table_name}")
        
        # Create success log message
        log_message = {
            "step" : "load",
            "component" : "staging",
            "status" : "success",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        
        # Create a failed log message
        log_message = {
            "step" : "load",
            "component" : "staging",
            "status" : "failed",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
        
        try:
            handle_error(data=data, bucket_name="paccafefailed", table_name=table_name)
        except Exception as e:
            print(e)
    finally:
        etl_log(log_message)