import os
import pandas as pd
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
from datetime import datetime
from pangres import upsert
from src.utils.helper import etl_log, handle_error

load_dotenv()

DWH_DB_HOST=os.getenv("DWH_POSTGRES_HOST")
DWH_DB_USER=os.getenv("DWH_POSTGRES_USER")
DWH_DB_PASSWORD=os.getenv("DWH_POSTGRES_PASSWORD")
DWH_DB_PORT=os.getenv("DWH_POSTGRES_PORT")
DWH_DB_NAME=os.getenv("DWH_POSTGRES_DB")

def load_warehouse(data, schema:str, table_name: str, idx_name:str):
    try:
        # create connection to database
        conn = create_engine(f"postgresql://{DWH_DB_USER}:{DWH_DB_PASSWORD}@{DWH_DB_HOST}:{DWH_DB_PORT}/{DWH_DB_NAME}")

        # set data index or primary key
        data = data.set_index(idx_name)

        # Do upsert (Update for existing data and Insert for new data)
        upsert(con = conn,
                df = data,
                table_name = table_name,
                schema = schema,
                if_row_exists = "update")

        # create success log message
        log_message = {
            "step" : "load",
            "component" : "warehouse",
            "status" : "success",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        # return data
    except Exception as e:

        #create fail log message
        log_message = {
            "step" : "load",
            "component" : "warehouse",
            "status" : "failed",
            "table_name" : table_name,
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
        # Handling error: save data to Object Storage
        try:
            handle_error(data = data, bucket_name='paccafefailed', table_name= table_name)
        except Exception as e:
            print(e)
    finally:
        etl_log(log_message)

