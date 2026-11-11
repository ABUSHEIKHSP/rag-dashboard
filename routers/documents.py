from fastapi import APIRouter, UploadFile, File
from pathlib import Path
import os

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

CHUNK_DIR = Path("chunks")
CHUNK_DIR.mkdir(exist_ok=True)

@router.post("/documents/upload", tags=["documents"])
async def upload_pfd(file: UploadFile = File(...)):
    file_location = UPLOAD_DIR / file.filename
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)

    return {
        "message": f"PDF '{file.filename}' uploaded successfully",
        "size": f"{len(content) / 1024:.2f} KB"
    }


@router.get("/documents/list", tags=["documents"])
async def list_pdf():
    return {
        "files": os.listdir(UPLOAD_DIR)
    }

@router.get("/documents/delete", tags=["documents"])
async def delete_pdf(file: str):
    file_path = UPLOAD_DIR / file

    if os.path.exists(file_path):
        os.remove(file_path)
        return f"{file_path} deleted successfully."
    else:
        return f"{file_path} does not exist."


