from fastapi import APIRouter, Request, UploadFile
from jinja2_fragments.fastapi import Jinja2Blocks
import pandas as pd
import io

templates = Jinja2Blocks(directory="app/templates")
router = APIRouter()

from app.utils import read_file


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@router.get("/tset")
def index(request: Request):
    return templates.TemplateResponse("tset/tsets.html", {"request": request})

@router.get("/tset/{ts_id}/upload")
def index(ts_id: int, request: Request):
    return templates.TemplateResponse("tset/edit_tset.html", {"request": request, "ts_id": ts_id})

@router.post("/tset/{ts_id}/upload")
async def index(ts_id: int, request: Request, bank_csv: UploadFile):

    contents = await bank_csv.read()

    df = pd.read_csv(io.BytesIO(contents))

    

    rows = df.to_dict(orient='records')
    rows_as_lists = [list(row.values()) for row in rows]
    headers = list(rows[0].keys()) if rows else []

    # raw_upload = df.to_html(classes='my-table-class', border=0)

    # df['Amount'] = df['Amount'].astype(float)

    print(rows)
    # Process rows (make HTTP requests)
    # results = await process_rows(rows)

    # Return the HTMX template response
    return templates.TemplateResponse("tset/tset.html", {
        "request": request,
        "rows": rows,
        "rows_as_lists": rows_as_lists,
        "headers": headers,
     #   "raw_upload": raw_upload,
        "ts_id": ts_id
    })


@router.get("/tset/{ts_id}/table")
def index(request: Request):
    return templates.TemplateResponse("tset/tset.html", {"request": request})

