from fastapi import UploadFile
from typing import List

async def read_file(file: UploadFile) -> List[str]:
    content = await file.read()
    rows = content.decode().splitlines()
    return rows
