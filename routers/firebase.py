from firebase_admin import credentials, initialize_app, storage
import firebase_admin
from fastapi import UploadFile, HTTPException,  APIRouter

router = APIRouter()

cred = credentials.Certificate("./farmer-market-bfef4-firebase-adminsdk-bhaks-8005068aa6.json")
if not firebase_admin._apps:
    initialize_app(cred, {"storageBucket": "farmer-market-bfef4.firebasestorage.app"})

@router.post("/upload/")
async def upload_file(file: UploadFile):
    bucket = storage.bucket()
    blob = bucket.blob(file.filename)
    try:
        # Upload the file to Firebase Storage
        blob.upload_from_string(await file.read(), content_type=file.content_type)
        # Make the file publicly accessible
        blob.make_public()
        return {"file_url": blob.public_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
