from internetarchive import upload, configure
from config import *
import asyncio, os

configure(ARCHIVE_ACCESS_KEY, ARCHIVE_SECRET_KEY)

async def upload_file(identifier, file_path):
    for _ in range(MAX_RETRIES):
        try:
            upload(identifier=identifier, files=[file_path])
            return f"https://archive.org/download/{identifier}/{os.path.basename(file_path)}"
        except:
            await asyncio.sleep(2)
    return None