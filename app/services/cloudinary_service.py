import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
import os

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

def subir_logo(file: UploadFile, tenant_id: int, old_public_id: str = None):
    if old_public_id:
        try:
            cloudinary.uploader.destroy(old_public_id)
        except Exception as e:
            print(f"Error borrando logo viejo: {e}")

    folder_path = f"drip_gestion/tenants/tenant_{tenant_id}"
    
    result = cloudinary.uploader.upload(
        file.file,
        folder=folder_path,
        overwrite=True
    )

    return {
        "logo_url": result.get("secure_url"),
        "logo_public_id": result.get("public_id")
    }