from fastapi import UploadFile
from typing import List
from app.DataManager import DataManager


async def read_file(file: UploadFile) -> List[str]:
    content = await file.read()
    rows = content.decode().splitlines()
    return rows

dbLoc = 'data/data.db'
