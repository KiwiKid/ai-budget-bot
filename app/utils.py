from fastapi import UploadFile
from typing import List
from app.DataManager import DataManager
from pandas import DataFrame, Grouper, to_timedelta, to_datetime
import json
import pandas as pd


async def read_file(file: UploadFile) -> List[str]:
    content = await file.read()
    rows = content.decode().splitlines()
    return rows

dbLoc = 'data/data.db'


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


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.strftime('%Y-%m-%d')
        return super().default(obj)
