from fastapi import FastAPI
from app.db.supabase import create_supabase_client
from fastapi import APIRouter, HTTPException, Request, Query
from mangum import Mangum
from pydantic import BaseModel
from app.processed_file_upload_manager import ProcessedFileUploadManager

app = FastAPI()
supabase = create_supabase_client()
from fastapi.middleware.cors import CORSMiddleware
# CORS settings
origins = [
    "http://localhost:3000",  # Replace with the actual URL of your frontend
    "https://s3.amazonaws.com",
    "https://file-picker-one.vercel.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/webhook")
async def handle_webhook(request: Request):
    headers = request.headers
    # Extract necessary headers
    webhook_data = {
        "channel_id": headers.get("x-goog-channel-id"),
        "resource_id": headers.get("x-goog-resource-id"),
        "resource_state": headers.get("x-goog-resource-state"),
        "resource_uri": headers.get("x-goog-resource-uri"),
        "message_number": headers.get("x-goog-message-number"),
        "channel_expiration": headers.get("x-goog-channel-expiration"),
        "channel_token": headers.get("x-goog-channel-token")
    }

    # Only proceed if resource_state is 'change'
    if webhook_data["resource_state"] != "change":
        return {"status": "ignored", "reason": "Resource state is not 'change'"}

    # Insert data into Supabase
    response = supabase.table("google_drive_webhooks").insert(webhook_data).execute()

    # Check for errors in the response
    if hasattr(response, 'error') and response.error:
        raise HTTPException(status_code=500, detail=str(response.error))

    return {"status": "success", "data": webhook_data}

class ProcessFilesRequest(BaseModel):
    file_metadata: dict
    provider_token: str
    
@app.post("/process_drive_entity")
async def process_drive_entity(request: Request, payload: ProcessFilesRequest):
    # Extract access_token from headers
    access_token = request.headers.get('Authorization', '').replace('Bearer ', '')
    # Check authentication
    user_info = supabase.auth.get_user(access_token)
    if not user_info:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    user_id = user_info.user.id
    file_manager = ProcessedFileUploadManager(user_id, payload.provider_token)
    file_manager.process_and_upload(payload.file_metadata['id'])
    return {"status": "success"}

api_router = APIRouter()
app.include_router(api_router)
handler = Mangum(app)