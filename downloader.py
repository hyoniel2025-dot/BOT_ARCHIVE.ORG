import aiohttp, time
from config import CHUNK_SIZE

async def download_file(url, filename, progress_callback=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            start = time.time()

            with open(filename, "wb") as f:
                async for chunk in resp.content.iter_chunked(CHUNK_SIZE):
                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback and total > 0:
                        elapsed = time.time() - start
                        speed = downloaded / elapsed if elapsed > 0 else 0
                        eta = (total - downloaded) / speed if speed > 0 else 0
                        percent = int(downloaded * 100 / total)
                        await progress_callback(percent, speed, eta)

    return filename