import os 
from uuid import uuid4

def save_upload_file(upload_file, destination_foler: str ) -> str:
    os.makedirs(destination_foler, exist_ok=True)
    file_ext = upload_file.filename.split(".")[-1]
    file_name = f"{uuid4()}.{file_ext}"
    file_path = os.path.join(destination_foler, file_name)

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return file_path