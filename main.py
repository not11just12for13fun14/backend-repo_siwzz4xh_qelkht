import os
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional

from database import db, create_document, get_documents
from schemas import (
    Parent, Teacher, Child, Message, DailyLog,
    LeaveRequest, MedicineRequest, AlbumItem, Notification, PickupCode
)

app = FastAPI(title="Wheremykidsat API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "Wheremykidsat API", "status": "ok"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

# Utility

def collection(name: str):
    return db[name]

# Parents, Teachers, Children basic create/list

@app.post("/parents")
async def create_parent(payload: Parent):
    _id = create_document("parent", payload)
    return {"id": _id}

@app.get("/parents")
async def list_parents():
    return get_documents("parent")

@app.post("/teachers")
async def create_teacher(payload: Teacher):
    _id = create_document("teacher", payload)
    return {"id": _id}

@app.get("/teachers")
async def list_teachers():
    return get_documents("teacher")

@app.post("/children")
async def create_child(payload: Child):
    _id = create_document("child", payload)
    return {"id": _id}

@app.get("/children")
async def list_children():
    return get_documents("child")

# Messages

@app.post("/messages")
async def send_message(payload: Message):
    payload.timestamp = payload.timestamp or datetime.now(timezone.utc)
    _id = create_document("message", payload)
    return {"id": _id}

@app.get("/messages")
async def get_messages(child_id: Optional[str] = None, limit: int = 50):
    filt = {"child_id": child_id} if child_id else {}
    docs = get_documents("message", filt, limit)
    return docs

# Daily logs

@app.post("/logs")
async def create_daily_log(payload: DailyLog):
    _id = create_document("dailylog", payload)
    return {"id": _id}

@app.get("/logs")
async def get_daily_logs(child_id: Optional[str] = None, date: Optional[str] = None, limit: int = 30):
    filt = {}
    if child_id:
        filt["child_id"] = child_id
    if date:
        filt["date"] = date
    return get_documents("dailylog", filt, limit)

# Leave requests

@app.post("/leave-requests")
async def create_leave_request(payload: LeaveRequest):
    _id = create_document("leaverequest", payload)
    return {"id": _id}

@app.get("/leave-requests")
async def list_leave_requests(child_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    filt = {}
    if child_id:
        filt["child_id"] = child_id
    if status:
        filt["status"] = status
    return get_documents("leaverequest", filt, limit)

@app.post("/leave-requests/{request_id}/approve")
async def approve_leave_request(request_id: str, note: Optional[str] = None):
    result = collection("leaverequest").update_one({"_id": {"$eq": __import__('bson').ObjectId(request_id)}}, {"$set": {"status": "approved", "teacher_note": note, "updated_at": datetime.now(timezone.utc)}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "approved"}

@app.post("/leave-requests/{request_id}/reject")
async def reject_leave_request(request_id: str, note: Optional[str] = None):
    result = collection("leaverequest").update_one({"_id": {"$eq": __import__('bson').ObjectId(request_id)}}, {"$set": {"status": "rejected", "teacher_note": note, "updated_at": datetime.now(timezone.utc)}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "rejected"}

# Medicine requests

@app.post("/medicine-requests")
async def create_medicine_request(payload: MedicineRequest):
    _id = create_document("medicinerequest", payload)
    return {"id": _id}

@app.get("/medicine-requests")
async def list_medicine_requests(child_id: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    filt = {}
    if child_id:
        filt["child_id"] = child_id
    if status:
        filt["status"] = status
    return get_documents("medicinerequest", filt, limit)

@app.post("/medicine-requests/{request_id}/confirm")
async def confirm_medicine(request_id: str, teacher: Optional[str] = None):
    now = datetime.now(timezone.utc)
    result = collection("medicinerequest").update_one({"_id": {"$eq": __import__('bson').ObjectId(request_id)}}, {"$set": {"status": "confirmed", "confirmed_at": now, "confirmed_by": teacher, "updated_at": now}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Request not found")
    return {"status": "confirmed", "confirmed_at": now.isoformat()}

# Album

@app.post("/album")
async def upload_album_item(payload: AlbumItem):
    _id = create_document("albumitem", payload)
    return {"id": _id}

@app.get("/album")
async def list_album(child_id: Optional[str] = None, class_id: Optional[str] = None, limit: int = 100):
    filt = {}
    if child_id:
        filt["child_id"] = child_id
    if class_id:
        filt["class_id"] = class_id
    return get_documents("albumitem", filt, limit)

# Notifications

@app.post("/notifications")
async def create_notification(payload: Notification):
    payload.created_at = payload.created_at or datetime.now(timezone.utc)
    _id = create_document("notification", payload)
    return {"id": _id}

@app.get("/notifications")
async def list_notifications(child_id: Optional[str] = None, limit: int = 100):
    filt = {"child_id": child_id} if child_id else {}
    return get_documents("notification", filt, limit)

# Pickup codes

@app.post("/pickup-codes")
async def create_pickup_code(payload: PickupCode):
    _id = create_document("pickupcode", payload)
    return {"id": _id}

@app.get("/pickup-codes")
async def list_pickup_codes(child_id: Optional[str] = None, code: Optional[str] = None, limit: int = 20):
    filt = {}
    if child_id:
        filt["child_id"] = child_id
    if code:
        filt["code"] = code
    return get_documents("pickupcode", filt, limit)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
