"""
Database Schemas for Wheremykidsat

Each Pydantic model maps to a MongoDB collection (lowercased class name).
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Parent(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None

class Teacher(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    class_id: Optional[str] = None

class Child(BaseModel):
    name: str
    nickname: Optional[str] = None
    birthdate: Optional[str] = None
    parent_id: Optional[str] = None
    class_id: Optional[str] = None
    avatar_url: Optional[str] = None

class Message(BaseModel):
    child_id: Optional[str] = None
    sender_role: str = Field(..., description="parent|teacher")
    sender_name: Optional[str] = None
    text: Optional[str] = None
    image_url: Optional[str] = None
    timestamp: Optional[datetime] = None

class DailyLog(BaseModel):
    child_id: Optional[str] = None
    date: str
    activity: Optional[str] = None
    meals: Optional[str] = None
    health: Optional[str] = None
    notes: Optional[str] = None

class LeaveRequest(BaseModel):
    child_id: Optional[str] = None
    date: str
    reason: Optional[str] = None
    status: str = Field("pending", description="pending|approved|rejected")
    teacher_note: Optional[str] = None

class MedicineRequest(BaseModel):
    child_id: Optional[str] = None
    drug_name: str
    dosage: str
    notes: Optional[str] = None
    photo_url: Optional[str] = None
    status: str = Field("pending", description="pending|confirmed")
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None

class AlbumItem(BaseModel):
    child_id: Optional[str] = None
    class_id: Optional[str] = None
    media_url: str
    media_type: str = Field("photo", description="photo|video")
    caption: Optional[str] = None
    taken_at: Optional[datetime] = None

class Notification(BaseModel):
    child_id: Optional[str] = None
    title: str
    body: Optional[str] = None
    type: str = Field("general", description="pickup|notice|medicine|general")
    created_at: Optional[datetime] = None

class PickupCode(BaseModel):
    child_id: Optional[str] = None
    code: str
    expires_at: Optional[datetime] = None
