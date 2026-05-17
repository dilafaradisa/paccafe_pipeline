import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from src.utils.helper import etl_log, extract_target

load_dotenv()

DWH_DB_HOST=os.getenv("DWH_POSTGRES_HOST")
DWH_DB_USER=os.getenv("DWH_POSTGRES_USER")
DWH_DB_PASSWORD=os.getenv("DWH_POSTGRES_PASSWORD")
DWH_DB_PORT=os.getenv("DWH_POSTGRES_PORT")
DWH_DB_NAME=os.getenv("DWH_POSTGRES_DB")

STG_DB_HOST=os.getenv("STG_POSTGRES_HOST")
STG_DB_USER=os.getenv("STG_POSTGRES_USER")
STG_DB_PASSWORD=os.getenv("STG_POSTGRES_PASSWORD")
STG_DB_PORT=os.getenv("STG_POSTGRES_PORT")
STG_DB_NAME=os.getenv("STG_POSTGRES_DB")

def transform_customers(data: pd.DataFrame) -> pd.DataFrame:
    try:
        # rename customer_id -> nk_customer_id
        data = data.rename(columns={"customer_id": "nk_customer_id"})

        # drop duplicates on customer_id
        data = data.drop_duplicates(subset="nk_customer_id")

        # handle minus value in loyalty_points
        data['loyalty_points'] = data['loyalty_points'].apply(lambda x: x if x >= 0 else 0)

        # null phone number -> unknown
        data['phone'] = data['phone'].fillna('unknown')

        # standardize name column to lowercase
        data['first_name'] = data['first_name'].str.lower()
        data['last_name'] = data['last_name'].str.lower()

        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "success",
            "table_name" : "customers",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return data

    except Exception as e:
        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "failed",
            "table_name" : "customers",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg":str(e)
        }
    finally:
        etl_log(log_msg=log_message)

def transform_employees(data: pd.DataFrame) -> pd.DataFrame:
    try:
        # rename employee_id -> nk_employee_id
        data = data.rename(columns={"employee_id": "nk_employee_id"})
        data = data.drop_duplicates(subset="nk_employee_id")

        # standardize hore date
        data['hire_date'] = pd.to_datetime(data['hire_date'])
        data['hire_date'] = data['hire_date'].dt.strftime('%Y%m%d').astype(int)
        
        # standardize name
        data['first_name'] = data['first_name'].str.lower()
        data['last_name'] = data['last_name'].str.lower()

        # standardize role
        valid_roles = ["cashier", "waitress", "manager", "waiter", "barista"]
        data['role'] = data['role'].apply(lambda x: x if x in valid_roles else 'unknown')


        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "success",
            "table_name" : "employees",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        return data

    except Exception as e:
        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "failed",
            "table_name" : "employees",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
    
    finally:
        etl_log(log_msg=log_message)

def transform_store_branch(data: pd.DataFrame) -> pd.DataFrame:
    
    try:
        data = data.rename(columns={"store_id": "nk_store_id"})
        data = data.drop_duplicates(subset="nk_store_id")
        
        # Replace selected column values to lowercase
        data['store_name'] = data['store_name'].str.lower()
        
        # Create a success log message
        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "success",
            "table_name" : "store_branch",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return data
        
    except Exception as e:
        
        # Create a failed log message
        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "failed",
            "table_name" : "store_branch",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
        
    finally:
        # Save the log message
        etl_log(log_message)      

def transform_products(data: pd.DataFrame) -> pd.DataFrame:
    try:
        # rename product_id
        data = data.rename(columns={"product_id": "nk_product_id"})
        data = data.drop_duplicates(subset="nk_product_id")

        data['product_name'] = data['product_name'].str.lower()
        data['category'] = data['category'].str.lower()
        data['store_branch'] = data['store_branch'].str.lower()
        
        # remove $ sign
        data['unit_price'] = data['unit_price'].str.replace(r'[^0-9.]','',regex=True)
        data['cost_price'] = data['cost_price'].str.replace(r'[^0-9.]','',regex=True)
        
        # cast the data type to a numeric
        data['unit_price'] = pd.to_numeric(data["unit_price"], errors="coerce")
        data['cost_price'] = pd.to_numeric(data["cost_price"], errors="coerce")

        # get sk_branch_id
        dim_store_branch = extract_target('dim_store_branch')
        data = data.merge(dim_store_branch[['sk_store_id', 'store_name']], how='left', left_on='store_id', right_on='store_name')
        
        # Create a success log message
        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "success",
            "table_name" : "products",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return data
        
    except Exception as e:
        
        # Create a failed log message
        log_message = {
            "step" : "transformation",
            "component" : "warehouse",
            "status" : "failed",
            "table_name" : "products",
            "etl_date" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg" : str(e)
        }
    
    finally:
        # Save the log message
        etl_log(log_message)

def transform_orders(data: pd.DataFrame) -> pd.DataFrame:
    try:
        print("Start transforming orders data...")
        data = data.rename(columns={"order_id": "nk_order_id"})
        data = data.drop_duplicates(subset="nk_order_id")

        # get sk_employee_id
        print("Extracting employee data for transformation...")
        dim_employees = extract_target('dim_employees')
        data = data.merge(dim_employees[['nk_employee_id', 'sk_employee_id']],left_on='employee_id',right_on='nk_employee_id',how='left')
        
        # get sk_customer_id
        dim_customers = extract_target('dim_customers')
        data = data.merge(dim_customers[['nk_customer_id', 'sk_customer_id']],left_on='customer_id',right_on='nk_customer_id',how='left')
        
        # standardize date format
        data['order_date'] = data['order_date'].dt.strftime('%Y%m%d').astype(int)
        
        # standardize payment method and order status
        data['payment_method'] = data['payment_method'].str.lower()
        data['order_status'] = data['order_status'].str.lower()
        
        # Drop unnecessary columns
        data = data.drop(columns=["employee_id", "nk_employee_id", "customer_id", "nk_customer_id"])
        
        # Create a success log message
        log_message = {
            "step": "warehouse",
            "component": "database",
            "status": "success",
            "table_name": "orders",
            "etl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return data
        
    except Exception as e:
        # Create a failed log message
        log_message = {
            "step": "warehouse",
            "component": "database",
            "status": "failed",
            "table_name": "orders",
            "etl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg": str(e)
        }
        
    finally:
        # Save the log message
        etl_log(log_message)

def transform_order_details(data: pd.DataFrame) -> pd.DataFrame:
    print("Start transforming order details data...")
    try:
        data = data.rename(columns={"order_id": "nk_order_id"})
        data = data.drop_duplicates(subset="nk_order_id")
        
        dim_products = extract_target('dim_products')
        data = data.merge(dim_products[['nk_product_id', 'sk_product_id']], left_on='product_id', right_on='nk_product_id', how='left')

        data = data.drop(columns=["product_id","order_detail_id", 'created_at'])

        print('order details transformed successfully')
        
        # Create a success log message
        log_message = {
            "step": "transformation",
            "component": "warehouse",
            "status": "success",
            "table_name": "order_details",
            "etl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return data
        
    except Exception as e:
        log_message = {
            "step": "transformation",
            "component": "warehouse",
            "status": "failed",
            "table_name": "order_details",
            "etl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg": str(e)
        }
        
    finally:
        etl_log(log_message)

def transform_inventory(data: pd.DataFrame) -> pd.DataFrame:
    try:
        data = data.rename(columns={"tracking_id": "nk_tracking_id"})
        data = data.drop_duplicates(subset="nk_tracking_id")

        # standardize reason
        data['reason'] = data['reason'].str.lower()

        data['change_date'] = data['change_date'].dt.strftime('%Y%m%d').astype(int)

        log_message = {
            "step": "transformation",
            "component": "warehouse",
            "status": "success",
            "table_name": "inventory",
            "etl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return data
        
    except Exception as e:
        log_message = {
            "step": "transformation",
            "component": "warehouse",
            "status": "failed",
            "table_name": "inventory",
            "etl_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_msg": str(e)
        }
        
    finally:
        etl_log(log_message)