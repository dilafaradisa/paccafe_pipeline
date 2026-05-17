import os
from dotenv import load_dotenv
from src.integration.warehouse.extract import extract_from_staging
from src.integration.warehouse.load import load_warehouse
from src.integration.warehouse.transform import transform_customers, transform_employees, transform_store_branch, transform_products, transform_orders, transform_order_details, transform_inventory

def warehouse_pipeline():
    # extract data from staging
    print("extracting data from staging...")
    df_customers = extract_from_staging(table_name="customers")
    df_employees = extract_from_staging(table_name="employees")
    df_store_branch = extract_from_staging(table_name="store_branch")
    df_products = extract_from_staging(table_name="products")
    df_orders = extract_from_staging(table_name="orders")
    df_order_details = extract_from_staging(table_name="order_details")
    df_inventory_tracking = extract_from_staging(table_name="inventory_tracking")

    print("transforming data...")
    # transform data
    dim_customers = transform_customers(df_customers)
    load_warehouse(data=dim_customers, table_name="dim_customers", schema='public',idx_name="nk_customer_id")

    dim_employees = transform_employees(df_employees)
    load_warehouse(data=dim_employees, table_name="dim_employees", schema='public', idx_name="nk_employee_id")

    dim_store_branch = transform_store_branch(df_store_branch)
    load_warehouse(data=dim_store_branch, table_name="dim_store_branch", schema='public', idx_name="nk_store_id")

    dim_products = transform_products(df_products)
    load_warehouse(data=dim_products, table_name="dim_products", schema='public', idx_name="nk_product_id")

    fct_inventory = transform_inventory(df_inventory_tracking)
    load_warehouse(data=fct_inventory, table_name="fct_inventory", schema='public', idx_name="nk_tracking_id")

    df_orders_transformed = transform_orders(df_orders)
    df_order_details_transformed = transform_order_details(df_order_details)

    fct_order = df_orders_transformed.merge(df_order_details_transformed, left_on='nk_order_id', right_on='nk_order_id', how='left')
    print(fct_order.head())
    load_warehouse(data=fct_order, table_name="fct_orders", schema='public', idx_name="nk_order_id")

    print("Data loaded to warehouse successfully")
