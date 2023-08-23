import time
import os

import simplejson as json
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse, Response
from app.utils import read_file, CustomJSONEncoder
from fastapi import APIRouter, Request, UploadFile
from jinja2_fragments.fastapi import Jinja2Blocks
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import io
from app.open_ai_client import OpenAIClient
from app.DataManager import DataManager
import uuid

from typing import List
from app.config import Settings
from app.transaction import TransactionsList, RawTransactionRow
import signal
import uuid
from collections import defaultdict

templates = Jinja2Blocks(directory="app/templates")
router = APIRouter()
userId = 'bd65600d-8669-4903-8a14-af88203add38'
aiClient = OpenAIClient(organization="org-79wTeMDwJKLtMWOcnQRg6ozv")

subscribers = {}
runEventLoop = True


def present_transactions(user_id, request, ts_id, page, limit, message, done):
    db = DataManager()

    transactions = db.get_transactions(
        user_id=user_id, ts_id=ts_id, page=page, limit=limit, negative_only=False)

    print(
        f"present_transactions - returning saved transaction: {len(transactions)} (user_id={userId}, ts_id={ts_id}, page={1}, limit={10}, negative_only={False})")
    return templates.TemplateResponse("tset/tres.html", {"request": request, "ts_id": ts_id, "transactions": transactions, "page": page, "limit": limit, "message": message, "done": done})


# def add_subscriber(ts_id, t_id, message):
#    if ts_id not in subscribers:
#        subscribers[ts_id] = {}
#    if t_id not in subscribers[ts_id]:
#        subscribers[ts_id][t_id] = []
#    subscribers[ts_id][t_id].append(message)


# def handle_termination_signal(signum, frame):
#     global runEventLoop
#     print("Received termination signal. Shutting down...")
#     runEventLoop = False
#
#
# signal.signal(signal.SIGINT, handle_termination_signal)
# signal.signal(signal.SIGTERM, handle_termination_signal)
#
#
# def event_stream():
#     global runEventLoop
#     while runEventLoop:
#      #   print(
#      #       f"checking  EVENT {ts_id}  {t_id}) {len(subscribers)}")
#
#         if ts_id in subscribers and t_id in subscribers[ts_id]:
#             while subscribers[ts_id][t_id]:
#                 print(f"firing EVENT (self, subscribers:{ts_id}  {t_id})")
#
#                 message = subscribers[ts_id][t_id].pop(0)
#                 yield f"event: {message['event']}\ndata: {message['data']}\n\n"
#         time.sleep(1)
#
#
# @router.get('/tset-events')
# async def sse():
#    return StreamingResponse(event_stream(), media_type="text/event-stream")
#
#


# @router.get("/")
# def index(request: Request):
#    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/tset/{ts_id}/status/{t_id}")
def index(ts_id: str, t_id: str, request: Request):
    db = DataManager()
    record = db.get_transaction(userId, t_id)
    return templates.TemplateResponse("tset/edit_tset.html", {"request": request, "ts_id": ts_id, })


@router.get("/")
def index(request: Request):
    db = DataManager()
    existingTransactionSet = db.get_transaction_sets_by_session(
        userId)
    return templates.TemplateResponse("tset/tsets.html", {"request": request, "sets": existingTransactionSet, "new_ts_id": str(uuid.uuid4())})


@router.get("/tset/{ts_id}")
def index(ts_id: str, request: Request):

    page = int(request.query_params.get('page', 1))
    limit = int(request.query_params.get('limit', 50))

    print(f"GET /tset/{ts_id}")
    return present_transactions(
        request=request, user_id=userId, ts_id=ts_id, page=page, limit=limit, message='', done=False)


@router.delete("/tset/{ts_id}/category")
def index(ts_id: str, request: Request):
    db = DataManager()
    db.reset_transaction_set(ts_id=ts_id)
    return Response(status_code=200, media_type="application/json")


@router.delete("/tset/{ts_id}/t_id/{t_id}/category")
def index(ts_id: str, t_id: str, request: Request):
    db = DataManager()
    res = db.reset_transaction(t_id=t_id)
    return Response(status_code=200, content={"deleted": 1, "t_id": res}, media_type="application/json")


@router.get("/tset/{ts_id}/upload")
def index(ts_id: str, request: Request):
    return templates.TemplateResponse("tset/edit_tset.html", {"request": request, "ts_id": ts_id})


@router.post('/tset/{ts_id}/categorize')
def index(ts_id: str, request: Request):
    db = DataManager()
    page = int(request.query_params.get('page', 0))
    limit = int(request.query_params.get('limit', 50))
    aiBatchLimit = min(int(request.query_params.get('limit', 20)), 20)
    transactions = db.get_transactions_to_process(
        userId, ts_id, page, aiBatchLimit)

    if not len(transactions) > 0:
        return present_transactions(
            request=request, user_id=userId, ts_id=ts_id, page=page, limit=limit, message="ALL PROCESSED", done=True)

    # for preT in transactions:
       # add_subscriber(preT[1], preT[0], {
       #     'event': 'start_category'
       # })

    response = aiClient.categorizeTransactions(transactions, [])
    aiRes = json.loads(response)
    processed = 0

    for cat in aiRes['categories']:
        db.set_transaction_category(t_id=cat['t_id'], category=cat['category'])
       # add_subscriber(ts_id, cat['t_id'], {
       #     'event': 'new_category',
       #     "data": {
       #         "category": cat['category'],
       #     }
       # })
        processed = processed + 1

    return present_transactions(
        request=request, user_id=userId, ts_id=ts_id, page=page, limit=limit, message="Done", done=False)

    # templates.TemplateResponse("tset/tres.html", {"request": request, "ts_id": ts_id, "transactions": transactions, "page": page, "limit": limit, "message": f"Processed {processed}", "done": False})

    # return templates.TemplateResponse('tset/tlink.html', {"request": request, "ts_id": ts_id, "response": response, "message": })


@router.get("/tset/{ts_id}/chart")
def chart_view_hx(ts_id: str, request: Request):
    """Returns chart options for echarts"""

    page = int(request.query_params.get('page', 0))
    limit = int(request.query_params.get('limit', 999))
    mode = int(request.query_params.get('mode', 1))
    groupBy = request.query_params.get('groupBy', 'week')

# 3
   # 3 days_in_period = {
   # 3     "week": 7,
   # 3     "month": 30,
   # 3 }
    db = DataManager()
    transactions = db.get_transactions(
        user_id=userId, ts_id=ts_id, page=page, limit=limit, negative_only=True)

    mode = 3
    if mode == 1:
        # Step 1: Create a dictionary to aggregate the amounts by category.
        #    category_amounts = {}
        #
        #    # Step 2: Iterate through the transactions.
        #    for transaction in transactions:
        #        print(f"transaction: {transaction}")
        #        category = transaction[7]
        #        amount = float(transaction[5]) * -1  # Assuming amount is stored as a string. Convert to float for calculations.
        #
        #        if category in category_amounts:
        #            category_amounts[category] += amount
        #        else:
        #            category_amounts[category] = amount
        #
        #        aggregated = aggregate_transactions(transactions, groupBy)
        #        categories = aggregated['category'].drop_duplicates().tolist()
        #        x_axis_dates = aggregated['date'].drop_duplicates().tolist()
        #        # Create a dictionary to store the series data
        #        series_data = []

        #        # Loop through each unique category and format its data
        #        for category in categories:
        #            category_data = {
        #                'name': category,
        #                'type': 'line',  # You can change the chart type if needed
        #                'data': aggregated[aggregated['category'] == category]['amount'].tolist()
        #            }
        #            series_data.append(category_data)

        #        # Final data structure for ECharts
        #        # echarts_formatted_data = {
        #        #    'x_axis': x_axis_dates,
        #        #    'series': series_data
        #        # }

        #        echarts_data = {
        #            "title": {
        #                "text": "Category Chart"
        #            },
        #            "tooltip": {},
        #            "legend": {
        #                "data": ["Transactions"]
        #            },
        #            "xAxis": {
        #                "data": x_axis_dates
        #            },
        #            "yAxis": {},
        #            "series": [{
        #                "name": "Sales",
        #                "type": "line ",
        #                "data": series_data,
        #            }]
        #        }

        #        return Response(status_code=200, content=json.dumps(echarts_data, cls=CustomJSONEncoder), media_type="application/json")

        #    elif mode == 2:
        #        # Collecting unique dates and categories
        #        aggregated = aggregate_transactions(transactions, groupBy)
        #        raw_categories = list(aggregated['category'])
        #        categories = list(dict.fromkeys(raw_categories))
        #        # For simplicity, we'll just extract dates from one category (assuming all categories have the same date keys)
        #        dates = [np.datetime_as_string(date, unit='D')
        #                 for date in sorted(aggregated['date'].values)]
        #        # This constructs a dictionary where each category corresponds to a list of amounts over the sorted dates
        #        # series_data = {category: [aggregated[category].get(date, 0) for date in dates] for category in categories}

        #        series = [{
        #            "name": category,
        #            "type": "line",
        #            "stack": "Total",
        #            "label": {"position": "outside"},
        #            "areaStyle": {},
        #            "data": data.tolist(),
        #            "emphasis": {
        #                "focus": 'series'
        #            },
        #        } for category, data in aggregated.items()]

        #        echarts_data = {
        #            "title": {
        #                "text": "Weekly Category Chart"
        #            },
        #            "tooltip": {
        #                "trigger": 'axis',
        #                "axisPointer": {
        #                    "type": 'cross',
        #                    "label": {
        #                        "backgroundColor": "#6a7985"
        #                    }
        #                }
        #            },
        #            "legend": {
        #                "data": categories
        #            },
        #            "xAxis": {
        #                "data": dates
        #            },
        #            "yAxis": {
        #                "type": "value"
        #            },
        #            "series": series
        #        }

        #        return Response(status_code=200, content=json.dumps(echarts_data), media_type="application/json")
        print(f"nah not doing it")
    else:
        return Response(status_code=400, content="No mode", media_type="application/text")
#    # optional
#    # if using the django_htmx library you can attach any clientside
#    # events here . For example

#    # trigger_client_ev


@router.post("/tset/{ts_id}/upload")
async def index(ts_id: str, request: Request, bank_csv: UploadFile):
    contents = await bank_csv.read()

    df = pd.read_csv(io.BytesIO(contents))

    rows = df.to_dict(orient='records')
    rows_as_lists = [list(row.values()) for row in rows]

    headers = list(rows[0].keys()) if rows else []

    db = DataManager()
    existingHeaders = db.get_header_by_session(userId)
    isExisting = True

    if not existingHeaders:
        print(f"no existing headers, calling openai")
        isExisting = False
        csv = df.to_csv(index=False)
        first_10_lines = "\n".join(csv.split("\n")[:10])

        gpt_message = [{
            "role": 'user',
            "content": first_10_lines,
        }]

        print(gpt_message)

        response = aiClient.getImportantHeaders(gpt_message)
        print(f"finished calling openai")
        # raw_upload = df.to_html(classes='my-table-class', border=0)

        # df['Amount'] = df['Amount'].astype(float)

        headersRes = json.loads(response)
        record = {
            "ts_id": ts_id,
            "user_id": userId,
            "amount_head": headersRes.get("amount"),
            "date_head": headersRes.get("date"),
            "description_head": headersRes.get("description"),
        }
        print(f"saving headers..")
        res = db.save_header(record)
        if res == 0:
            print(f"Could not save header")
            raise 'Could not save header'
        print(f"headers saved")
        existingHeaders = db.get_header_by_session(user_id=userId)
        print(f"retrieved existingHeaders: {len(existingHeaders)}")

    for row in rows:
        t_id = str(uuid.uuid4())
        amount: str = str(row[existingHeaders[0][2]])
        date: str = row[existingHeaders[0][3]]
        headers = existingHeaders[0][4].split('|')

        description_parts = [str(row[header])
                             for header in headers if header in row]

        removals = ['nan', 'Df']
        for idx, part in enumerate(description_parts):
            for rem in removals:
                part = part.replace(rem, ' ')
            description_parts[idx] = part.strip()

        description = ' '.join(description_parts).strip()

        print(f"saving transaction")
        trans = db.save_transaction(t_id=t_id, ts_id=ts_id, user_id=userId, amount=float(amount),
                                    date=date, description=description, status='pending')
        print(f"saved transaction {trans.returns_rows}")

    doubleCheckSave = db.get_transaction_sets_by_session(userId)

    print(f"saved transaction sets {doubleCheckSave[0].count}")

    # Process rows (make HTTP requests)

    # results = await process_rows(rows_as_lists)

    # TRY/TEMP use present transactions

    return present_transactions(userId, request, ts_id=ts_id, page=0, limit=100, message='', done=False)
    # Return the HTMX template response
    return templates.TemplateResponse("tset/tset.html", {
        "request": request,
        "rows": rows,
        "rows_as_lists": rows_as_lists,
        "transactions": transactions,
        "headers": headers,
        #   "raw_upload": raw_upload,
        "ts_id": ts_id,
        "header_set": existingHeaders,
        "is_existing": isExisting,
        "save_count": len(rows)
    })


@router.get("/tset/{ts_id}/table")
def index(request: Request):
    return templates.TemplateResponse("tset/tset.html", {"request": request})
