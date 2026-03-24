import py7zr, os
from config import VOLUME_SIZE

def compress_and_split(file_path):
    archive = file_path + ".7z"

    with py7zr.SevenZipFile(archive, 'w') as z:
        z.write(file_path)

    parts = []
    with open(archive, "rb") as f:
        i = 0
        while True:
            chunk = f.read(VOLUME_SIZE)
            if not chunk:
                break
            part = f"{archive}.part{i}"
            with open(part, "wb") as p:
                p.write(chunk)
            parts.append(part)
            i += 1

    os.remove(archive)
    return parts