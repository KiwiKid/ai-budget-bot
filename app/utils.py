import os
from fastapi import UploadFile
from typing import List, Dict
from pandas import DataFrame, Grouper, to_timedelta, to_datetime
import json
import pandas as pd
from dotenv import load_dotenv, find_dotenv


from collections import defaultdict


def transactions_to_chartjs(transactions):
    # Initialize a dictionary with 0 for each category
    data_dict = defaultdict(float)
    for tran in transactions:
        # Use dot notation instead of square bracket notation
        if not tran.category:
            cat = 'Uncategorized'
        else:
            cat = tran.category
        data_dict[cat] += float(tran.amount)

    # Separate data into labels and data for ChartJS
    labels = list(data_dict.keys())
    data = list(data_dict.values())

    return labels, data


def pg_array_to_python_list(array_str: str) -> list:
    if array_str == None:
        return []

    items = array_str.split(",")

    cleaned_items = []
    for item in items:
        # Remove surrounding quotes if present
        if item.startswith('"') and item.endswith('"'):
            item = item[1:-1]

        # Strip any surrounding curly braces
        item = item.strip('{}')

        cleaned_items.append(item)

    return cleaned_items


async def read_file(file: UploadFile) -> List[str]:
    content = await file.read()
    rows = content.decode().splitlines()
    return rows

dbLoc = 'data/data.db'
debug = os.getenv('DEBUG')


# def aggregate_transactions(transactions, breakdown="day"):
#     # Convert transactions list into a DataFrame
#     df = DataFrame(transactions, columns=['t_id', 'ts_id', 'user_id', 'date', 'description', 'amount', 'status', 'category', 'created_at'])
#     df['date'] = to_datetime(df['date'],format='%d/%m/%Y')
#     df['amount'] = df['amount'].astype(float) * -1#3333333333333
#     # Aggregate data based on breakdown
#     if breakdown == "week":
#         df['date'] = df['date'] - to_timedelta(7, unit='d')
#         grouped = df.groupby([Grouper(key='date', freq='W-MON'), 'category']).sum().reset_index()
#     elif breakdown == "month":
#         grouped = df.groupby([Grouper(key='date', freq='M'), 'category']).sum().reset_index()
#     elif breakdown == "year":
#         grouped = df.groupby([Grouper(key='date', freq='A'), 'category']).sum().reset_index()
#     else:  # default is day
#         grouped = df.groupby(['date', 'category']).sum().reset_index()#3333333333333
#     return grouped


def load_dotenv_safe():
    # Load the .env file
    load_dotenv(find_dotenv())

    current_directory = os.path.dirname(os.path.abspath(__file__))
    env_example_path = os.path.join(current_directory, '.env.example')
    print("load_dotenv_safe path: ")
    print(os.getcwd())

    # Load the .env.example file to get a list of required keys
    with open(env_example_path, 'r') as f:
        required_keys = [line.split('=')[0] for line in f if line.strip()]

    # Check each required key
    for key in required_keys:
        if key not in os.environ:
            raise EnvironmentError(f"Environment variable {key} not set")
        elif debug:
            print(f"{key} found in env")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)


def flatten_form_data(form_data: Dict[str, str], field_prefix: str) -> List[str]:
    """
    Flattens form data based on a given field prefix.
    For example, for the field_prefix 'description', it would combine
    'description[0]', 'description[1]', ... into a list of values.
    """
    result = []
    for key, value in form_data.items():
        if key.startswith(field_prefix):
            result.append(value)
    return result
