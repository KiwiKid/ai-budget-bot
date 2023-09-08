import time
import os
from pydantic import BaseModel
import simplejson as json
from datetime import datetime, timedelta
from fastapi.responses import StreamingResponse, Response
from app.utils import read_file, CustomJSONEncoder, flatten_form_data
from fastapi import APIRouter, Request, UploadFile, Form
from jinja2_fragments.fastapi import Jinja2Blocks
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import io
from app.open_ai_client import OpenAIClient
from app.DataManager import DataManager
import uuid

from typing import List, Optional
from app.config import Settings
from app.URLGenerator import URLGenerator
import signal
import uuid
from collections import defaultdict

templates = Jinja2Blocks(directory="app/templates")
router = APIRouter()
userId = 'bd65600d-8669-4903-8a14-af88203add38'
aiClient = OpenAIClient()

subscribers = {}
runEventLoop = True


class HeaderData(BaseModel):
    amount: str
    date: str
    description: Optional[List[str]]
    custom_rules: Optional[str]
    custom_categories: Optional[List[str]]
    custom_categories_new: Optional[str]


def clean_description(description_parts, removals):
    cleaned_parts = []

    for part in description_parts:
        for rem in removals:
            # Remove unwanted substrings from each part
            part = part.replace(rem, '')
        # Add the cleaned part to the new list
        cleaned_parts.append(part.strip())

    # Join the cleaned parts back together, and remove any extra spaces
    return ' '.join(cleaned_parts).strip()


def present_transactions(user_id: str, request, ts_id: str, page: int, limit: int, message: str, done, expanded):
    db = DataManager()

    transactions = db.get_transactions(
        user_id=user_id, ts_id=ts_id, page=page, limit=limit, negative_only=False)

    transactions_stats = db.get_transaction_sets_by_session(
        user_id=user_id, ts_id=ts_id)

    print(
        f"present_transactions - returning saved transactions: {len(transactions)} for set {ts_id} (user_id={userId}, ts_id={ts_id}, page={1}, limit={10}, negative_only={False})")

    transaction_dicts = [ts.to_dict() for ts in transactions_stats]

    grandTotal = sum(ts['total']
                     for ts in transaction_dicts if 'total' in ts)

    total_rows = sum(ts['count']
                     for ts in transaction_dicts if 'count' in ts)

    urlGen = URLGenerator(base_url=f'/tset/{ ts_id }', expanded=expanded)

   # $3 eariest_date =
   # $3 latest_date =

    return templates.TemplateResponse("tset/tres.html",
                                      {"request": request,
                                       "ts_id": ts_id,
                                       "transactions": transactions,
                                       "page": page,
                                       "limit": limit,
                                       "message": message,
                                       "done": done,
                                       "stats": transaction_dicts,
                                       "grand_total": grandTotal,
                                       "expanded": expanded,
                                       "next_page": urlGen.generate_next(page, limit, total_rows),
                                       "prev_page": urlGen.generate_prev(page, limit),
                                       'header_form_url': urlGen.generate_headers_url(ts_id=ts_id)
                                       })


def present_headers(user_id, request, ts_id, message):
    db = DataManager()
    headers = db.get_header(user_id=user_id, ts_id=ts_id)

    if not headers:
        raise "no headers to raise"

  # if len(headers.custom_categories) == 0 or headers.custom_categories[0] == '':
  #     overrideCategories = [
  #         'Housing',
  #         'Groceries',
  #         'Eating Out',
  #         'Transportation',
  #         'Healthcare',
  #         'Entertainment',
  #         'Apparel',
  #         'Income',
  #         'Debts'
  #     ]
  # else:
  #     overrideCategories = headers.custom_categories

    return templates.TemplateResponse("edit_header.html", {
        "message": message,
        'request': request,
        'ts_id': headers.ts_id,
        'amount_head': headers.amount_head,
        'date_head': headers.date_head,
        'description_head': headers.description_head,
        'custom_rules': headers.custom_rules,
        'custom_categories': headers.custom_categories
    })

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
    return templates.TemplateResponse("index.html", {"request": request, "new_ts_id": str(uuid.uuid4())})


@router.get("/tsets")
def index(request: Request):
    db = DataManager()
    existingTransactionSet = db.get_transaction_sets_by_session(
        userId)
    return templates.TemplateResponse("tset/tsets.html", {"request": request, "sets": existingTransactionSet})


@router.get("/tset/{ts_id}")
def index(ts_id: str, request: Request):

    page = int(request.query_params.get('page', 0))
    limit = int(request.query_params.get('limit', 50))
    expanded = request.query_params.get('expanded', False) == 'true'

    print(f"GET /tset/{ts_id}")
    return present_transactions(
        request=request, user_id=userId, ts_id=ts_id, page=page, limit=limit, message='', done=False, expanded=expanded)


@router.delete("/tset/{ts_id}")
def index(ts_id: str, request: Request):

    db = DataManager()
    db.delete_transaction_set(ts_id=ts_id)
    return Response(status_code=200, headers={'HX-Redirect': '/'}, media_type="application/json")


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


@router.get("/sidebar")
def index(request: Request):

    page = int(request.query_params.get('page', 0))
    limit = int(request.query_params.get('limit', 50))
    expanded = request.query_params.get('expanded', False) == 'true'

    urlGen = URLGenerator(base_url=f'', expanded=expanded)

    return templates.TemplateResponse("shared/sidebar.html", {"request": request,
                                                              'page': page,
                                                              'limit': limit,
                                                              "expanded": expanded,
                                                              "new_ts_id": str(uuid.uuid4()),
                                                              "sidebar_url": urlGen.generate_side_bar_url(),
                                                              "new_upload_path": urlGen.generate_upload_url(str(uuid.uuid4())),
                                                              })


@router.post('/tset/{ts_id}/categorize')
def index(ts_id: str, request: Request):
    db = DataManager()
    page = int(request.query_params.get('page', 0))
    limit = int(request.query_params.get('limit', 50))
    expanded = request.query_params.get('expanded', False) == 'true'

    aiBatchLimit = min(int(request.query_params.get('limit', 20)), 20)
    transactions = db.get_transactions_to_process(
        userId, ts_id, page, aiBatchLimit)

    if not len(transactions) > 0:
        return present_transactions(
            request=request, user_id=userId, ts_id=ts_id, page=page, limit=limit, message="ALL PROCESSED", done=True, expanded=expanded)

    # for preT in transactions:
       # add_subscriber(preT[1], preT[0], {
       #     'event': 'start_category'
       # })

    headers = db.get_header(user_id=userId, ts_id=ts_id)

    print(
        f"categorize transactions {len(transactions)} with overrideCategories {headers.custom_categories} and rules: {headers.custom_rules}")
    response = aiClient.categorizeTransactions(
        transactions, overrideCategories=headers.custom_categories, custom_rules=headers.custom_rules)
    print(f"categorized transactions - Got: {len(response['categories'])}")
    processed = 0

    for cat in response['categories']:
        db.set_transaction_category(t_id=cat['t_id'], category=cat['category'])
        print(
            f"set_transaction_category(t_id={cat['t_id']}, category={cat['category']})")
       # add_subscriber(ts_id, cat['t_id'], {
       #     'event': 'new_category',
       #     "data": {
       #         "category": cat['category'],
       #     }
       # })
        processed = processed + 1

    return present_transactions(
        request=request, user_id=userId, ts_id=ts_id, page=page, limit=limit, message="Done", done=False, expanded=expanded)

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


@router.get("/api/tset/{ts_id}/headers")
def get_headers(
    ts_id: str,
    request: Request
):
    return present_headers(user_id=userId, request=request, ts_id=ts_id, message='')


@router.put("/api/tset/{ts_id}/headers")
async def update_headers(
    ts_id: str,
    request: Request
    #  request: Request,
    #  amount: str = Form(...),
    #  date: str = Form(...),
    #  description: Optional[List[str]] = Form(None),
    # custom_rules: Optional[List[str]] = Form(None),
    #  custom_categories: Optional[List[str]] = Form(None),
    # custom_categories_new: Optional[str] = Form(None)
):
  # try:
  #     custom_categories = json.loads(custom_categories)
  #     if isinstance(custom_categories, bytes):
  #         custom_categories = custom_categories.decode('utf-8')
  # except json.JSONDecodeError:
  #     # Handle the error as you see fit (logging, returning an error response, etc.)
  #     return present_headers(user_id=userId, request=request, ts_id=ts_id, message="Invalid JSON format for custom_categories")

    db = DataManager()

    form_data = dict(await request.form())

    # Extract the fields from form_data
    amount = form_data.get('amount')
    date = form_data.get('date')
    custom_categories_new = form_data.get('custom_categories_new')

    description = flatten_form_data(form_data, 'description')
    custom_rules = flatten_form_data(form_data, 'custom_rules')
    custom_categories = flatten_form_data(form_data, 'custom_categories')

    if custom_categories_new is not None and custom_categories_new != '':
        custom_categories.append(custom_categories_new)

    categoriesToSave = [
        category for category in custom_categories if category != '']

    record = {
        "ts_id": ts_id,
        "amount_head": amount,
        'user_id': userId,
        "date_head": date,
        "description_head": description,
        'custom_rules': custom_rules,
        'custom_categories': categoriesToSave
    }

    # Assuming db.save_header returns a response indicating success
    res = db.save_header(record)

    if res:
        return present_headers(user_id=userId, request=request, ts_id=ts_id, message='')
    else:
        return present_headers(user_id=userId, request=request, ts_id=ts_id, message='error saving form')


@router.post("/tset/{ts_id}/upload")
async def index(ts_id: str, request: Request, bank_csv: UploadFile):

    contents = await bank_csv.read()
    expanded = request.query_params.get('expanded', False) == 'true'

    df = pd.read_csv(io.BytesIO(contents))

    rows = df.to_dict(orient='records')
    rows_as_lists = [list(row.values()) for row in rows]

    headers = list(rows[0].keys()) if rows else []

    db = DataManager()
    existingHeaders = db.get_header(user_id=userId, ts_id=ts_id)

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
            'custom_rules': '',
            'custom_categories': ''
        }
        saveHeader = db.save_header(record)
        if saveHeader is None:
            print(f"Could not save header")
            raise Exception('Could not save header')
        print(f"headers saved")
        existingHeaders = db.get_header(user_id=userId, ts_id=ts_id)
        print(f"retrieved existingHeaders: {existingHeaders}")

    for row in rows:
        t_id = str(uuid.uuid4())
        amount: str = str(row[existingHeaders.amount_head])
        date: str = row[existingHeaders.date_head]
        descriptionFields = existingHeaders.description_head

        description_parts = [str(row[header])
                             for header in descriptionFields if header in row]

        description = clean_description(
            description_parts, ['nan', 'Df'])

        print(f"saving transaction")
        trans = db.save_transaction(t_id=t_id, ts_id=ts_id, user_id=userId, amount=float(amount),
                                    date=date, description=description, status='pending')
        print(f"saved transaction {trans}")

    return present_transactions(userId, request, ts_id=ts_id, page=0, limit=100, message='', done=False, expanded=expanded)


@router.get("/tset/{ts_id}/table")
def index(request: Request):
    return templates.TemplateResponse("tset/tset.html", {"request": request})
