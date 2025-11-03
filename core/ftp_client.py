import ftplib
import uuid
from fastapi import UploadFile
from PIL import Image
import io

class FTPClient:
    def __init__(self):
        self.host = "103.28.36.219"  # Hoặc "ftp.chodenpubgpc.com"
        self.port = 21
        self.username = "nhchosv0"  # USERNAME CHÍNH
        self.password = "%_BWBkFkmvP32^6@"  # PASSWORD CỦA NHCHOSV0
        self.ftp_upload_dir = "/public_html/uploads/"  # UPLOAD VÀO WEB DIRECTORY
        self.web_access_url = "https://chodenpubgpc.com/uploads/"

    async def optimize_image(self, file: UploadFile) -> tuple[bytes, str]:
        """Tối ưu ảnh: resize + compress + convert WebP"""
        try:
            # Đọc ảnh gốc
            image_data = await file.read()
            image = Image.open(io.BytesIO(image_data))
            
            # Giữ metadata orientation
            image = ImageOps.exif_transpose(image)
            
            # Resize nếu ảnh quá lớn (max 1200px)
            max_size = 1200
            if max(image.size) > max_size:
                image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert sang WebP (tiết kiệm 30% so với JPEG)
            output = io.BytesIO()
            image.save(output, format='WEBP', quality=80, optimize=True)
            
            return output.getvalue(), 'webp'
            
        except Exception as e:
            print(f"❌ Image optimization error: {e}")
            # Fallback: trả về ảnh gốc
            await file.seek(0)
            return await file.read(), file.filename.split('.')[-1]

    async def upload_image(self, file: UploadFile) -> str:
        try:
            print("🔄 Optimizing image...")
            optimized_data, ext = await self.optimize_image(file)
            
            print("🔗 Connecting to FTP...")
            ftp = ftplib.FTP()
            ftp.connect(self.host, self.port)
            ftp.login(self.username, self.password)
            ftp.cwd(self.ftp_upload_dir)
            
            # Tạo tên file với extension đúng
            filename = f"img_{uuid.uuid4()}.{ext}"
            print(f"📤 Uploading optimized image: {filename}")
            
            # Upload ảnh đã tối ưu
            bio = io.BytesIO(optimized_data)
            ftp.storbinary(f"STOR {filename}", bio)
            ftp.quit()
            
            image_url = f"{self.web_access_url}{filename}"
            print(f"🎉 Upload successful: {image_url}")
            return image_url
            
        except Exception as e:
            print(f"💥 FTP Upload error: {e}")
            raise e