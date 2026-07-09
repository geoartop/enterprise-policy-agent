import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data" / "input"

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Handles PDF uploads and writes them to the local data directory.
    
    Args:
        file (UploadFile): The uploaded file object (must be a PDF). Defaults to File(...).
        
    Returns:
        dict: A dictionary containing the filename, relative path, and a success message.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / file.filename
    
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    relative_path = f"data/input/{file.filename}"
    return {"filename": file.filename, "path": relative_path, "message": "File uploaded successfully"}
