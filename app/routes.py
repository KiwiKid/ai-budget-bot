import json
import os
import time
from fastapi.responses import StreamingResponse
from app.utils import read_file
from fastapi import APIRouter, Request, UploadFile
from jinja2_fragments.fastapi import Jinja2Blocks
from jinja2 import Environment, FileSystemLoader
import pandas as pd
import io
from app.open_ai_client import OpenAIClient
from app.DataManager import DataManager
import uuid
from app.enumerate_filter import enumerate_filter
from typing import List
from app.config import Settings
from app.transaction import TransactionsList, RawTransactionRow

templates = Jinja2Blocks(directory="app/templates")
router = APIRouter()
userId = 'bd65600d-8669-4903-8a14-af88203add38'
aiClient = OpenAIClient(organization="org-79wTeMDwJKLtMWOcnQRg6ozv")
dbLoc = 'data/data.db'

subscribers = {}


def add_subscriber(ts_id, t_id, message):
    if ts_id not in subscribers:
        subscribers[ts_id] = {}
    if t_id not in subscribers[ts_id]:
        subscribers[ts_id][t_id] = []
    subscribers[ts_id][t_id].append(message)


def event_stream(ts_id, t_id):
    while True:
        print(
            f"checking  EVENT {ts_id}  {t_id}) {len(subscribers)} {len(subscribers[ts_id])}")

        if ts_id in subscribers and t_id in subscribers[ts_id]:
            while subscribers[ts_id][t_id]:
                print(f"firing EVENT (self, subscribers:{ts_id}  {t_id})")

                message = subscribers[ts_id][t_id].pop(0)
                yield f"event: {message['event']}\ndata: {message['data']}\n\n"
        time.sleep(1)


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/tset/{ts_id}/status/{t_id}")
def index(ts_id: str, t_id: str, request: Request):
    db = DataManager(dbLoc)
    record = db.get_transaction(userId, t_id)
    return templates.TemplateResponse("tset/edit_tset.html", {"request": request, "ts_id": ts_id, })


@router.get("/tset")
def index(request: Request):
    db = DataManager(dbLoc)
    existingTransactionSet = db.get_transactions_by_session(
        userId)
    return templates.TemplateResponse("tset/tsets.html", {"request": request, "sets": existingTransactionSet})


@router.get('/tset/{ts_id}/tid/{t_id}/events')
async def sse(ts_id: str, t_id: str):
    return StreamingResponse(event_stream(ts_id, t_id), media_type="text/event-stream")


@router.get("/tset/{ts_id}")
def index(ts_id: str, request: Request):
    db = DataManager(dbLoc)
    page = int(request.query_params.get('page', 0))
    limit = int(request.query_params.get('limit', 50))

    transactions = db.get_transactions(
        userId, ts_id, page, limit)
    return templates.TemplateResponse("tset/tres.html", {"request": request, "ts_id": ts_id, "transactions": transactions, "page": page, "limit": limit})


@router.get("/tset/{ts_id}/upload")
def index(ts_id: str, request: Request):
    return templates.TemplateResponse("tset/edit_tset.html", {"request": request, "ts_id": ts_id})


@router.post('/tset/{ts_id}/categorize')
def index(ts_id: str, request: Request):
    db = DataManager(dbLoc)
    page = int(request.query_params.get('page', 0))
    limit = min(int(request.query_params.get('limit', 20)), 20)
    transactions = db.get_transactions_to_process(userId, ts_id, page, limit)

    for preT in transactions:
        add_subscriber(preT[1], preT[0], {
            'event': 'start_category'
        })

    response = aiClient.categorizeTransactions(transactions, [])
    aiRes = json.loads(response)

    for cat in aiRes['categories']:
        db.set_transaction_category(t_id=cat['t_id'], category=cat['category'])
        add_subscriber(ts_id, cat['t_id'], {
            'event': 'new_category',
            "data": {
                "category": cat['category'],
            }
        })

    return templates.TemplateResponse('tset/tlink.html', {"request": request, "ts_id": ts_id, "response": response})


@router.post("/tset/{ts_id}/upload")
async def index(ts_id: str, request: Request, bank_csv: UploadFile):
    contents = await bank_csv.read()

    df = pd.read_csv(io.BytesIO(contents))

    rows = df.to_dict(orient='records')
    rows_as_lists = [list(row.values()) for row in rows]

    headers = list(rows[0].keys()) if rows else []

    db = DataManager(dbLoc)
    existingHeaders = db.get_header_by_session(userId)
    isExisting = True

    if not existingHeaders:
        isExisting = False
        csv = df.to_csv(index=False)
        first_10_lines = "\n".join(csv.split("\n")[:10])

        gpt_message = [{
            "role": 'user',
            "content": first_10_lines,
        }]

        print(gpt_message)

        response = aiClient.getImportantHeaders(gpt_message)

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
        db.save_header(record)
        existingHeaders = db.get_header_by_session(user_id=userId)

    for row in rows:
        t_id = str(uuid.uuid4())
        amount: str = str(row[existingHeaders[0][2]])
        date: str = row[existingHeaders[0][3]]
        headers = existingHeaders[0][4].split('|')

        description_parts = [str(row[header])
                             for header in headers if header in row]

        description: str = ' '.join(
            description_parts).replace('nan', ' ').strip()

        save_res = db.save_transaction(t_id=t_id, ts_id=ts_id, user_id=userId, amount=amount,
                                       date=date, description=description, status='pending')

        save_count = save_res
        print(save_res)

    # Process rows (make HTTP requests)

   # results = await process_rows(rows_as_lists)

   #
    # transactions = db.get_transactions(user_id=userId, ts_id=ts_id, limit=999)

    # Return the HTMX template response
    return templates.TemplateResponse("tset/tset.html", {
        "request": request,
        "rows": rows,
        "rows_as_lists": rows_as_lists,
        #   "transactions": transactions,
        "headers": headers,
        #   "raw_upload": raw_upload,
        "ts_id": ts_id,
        "header_set": existingHeaders,
        "is_existing": isExisting,
        "save_count": save_count
    })


@router.get("/tset/{ts_id}/table")
def index(request: Request):
    return templates.TemplateResponse("tset/tset.html", {"request": request})
