from fastapi import APIRouter, UploadFile, File, HTTPException
from core.ftp_client import FTPClient

router = APIRouter()

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "Chỉ chấp nhận file ảnh")
    
    try:
        ftp_client = FTPClient()
        image_url = await ftp_client.upload_image(file)
        
        return {
            "success": True, 
            "url": image_url,
            "filename": image_url.split("/")[-1]
        }
    except Exception as e:
        raise HTTPException(500, f"Upload thất bại: {str(e)}")