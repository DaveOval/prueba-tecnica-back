import os 
from uuid import uuid4

def normalize_path(path: str) -> str:
    """Normalize path to use forward slashes and remove any double slashes."""
    return os.path.normpath(path).replace("\\", "/")

def save_upload_file(upload_file, destination_folder: str) -> str:
    os.makedirs(destination_folder, exist_ok=True)
    file_ext = upload_file.filename.split(".")[-1]
    file_name = f"{uuid4()}.{file_ext}"
    file_path = normalize_path(os.path.join(destination_folder, file_name))

    with open(file_path, "wb") as buffer:
        buffer.write(upload_file.file.read())

    return file_path