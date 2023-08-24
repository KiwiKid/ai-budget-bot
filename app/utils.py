import os
from fastapi import UploadFile
from typing import List
from pandas import DataFrame, Grouper, to_timedelta, to_datetime
import json
import pandas as pd
from dotenv import load_dotenv, find_dotenv


def pg_array_to_python_list(array_str):
    return [item.strip('{}') for item in array_str.split(",")]


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
