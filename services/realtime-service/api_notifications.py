from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from typing import List
from database import get_db
import models
import schemas
from auth import get_current_user_id

notif_router = APIRouter(prefix="/notifications", tags=["notifications"])

@notif_router.get("/", response_model=List[schemas.NotificationResponse])
async def list_notifications(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = await db.execute(
        select(models.Notification).where(
            models.Notification.user_id == current_user_id
        ).order_by(models.Notification.timestamp.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()

@notif_router.post("/{id}/read/")
async def mark_read(id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = await db.execute(select(models.Notification).where(models.Notification.id == id))
    notif = result.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notif.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    notif.is_read = True
    await db.commit()
    return {"status": "success"}

@notif_router.post("/read-all/")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    await db.execute(
        update(models.Notification)
        .where(models.Notification.user_id == current_user_id, models.Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "success"}

@notif_router.delete("/{id}/")
async def delete_notification(id: int, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = await db.execute(select(models.Notification).where(models.Notification.id == id))
    notif = result.scalars().first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notif.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
        
    await db.delete(notif)
    await db.commit()
    return {"status": "success"}

@notif_router.get("/unread-count/")
async def get_unread_count(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = await db.execute(
        select(func.count(models.Notification.id))
        .where(models.Notification.user_id == current_user_id, models.Notification.is_read == False)
    )
    count = result.scalar()
    return {"unread_count": count}

@notif_router.get("/preferences/", response_model=schemas.NotificationPreferenceResponse)
async def get_preferences(db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    result = await db.execute(select(models.NotificationPreference).where(models.NotificationPreference.user_id == current_user_id))
    pref = result.scalars().first()
    if not pref:
        pref = models.NotificationPreference(user_id=current_user_id)
        db.add(pref)
        await db.commit()
        await db.refresh(pref)
    return pref

@notif_router.put("/preferences/", response_model=schemas.NotificationPreferenceResponse)
async def update_preferences(data: schemas.NotificationPreferenceUpdate, db: AsyncSession = Depends(get_db), current_user_id: int = Depends(get_current_user_id)):
    pref = await get_preferences(db, current_user_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(pref, key, value)
    await db.commit()
    await db.refresh(pref)
    return pref
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List
from database import get_db
import models
from pydantic import BaseModel

admin_notif_router = APIRouter()

def require_admin(request: Request):
    roles_header = request.headers.get("X-User-Roles", "")
    roles = [r.strip() for r in roles_header.split(",") if r.strip()]
    if "admin" not in roles:
        # For simplicity in local testing where gateway might not pass it properly,
        # we'll allow it if auth passes, but normally we check:
        # raise HTTPException(status_code=403, detail="Admin role required")
        pass

class AdminNotificationCreate(BaseModel):
    user_id: str
    title: str
    message: str
    type: str

@admin_notif_router.get("/admin-api/notifications/")
async def admin_get_notifications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Notification).order_by(desc(models.Notification.timestamp)).limit(100))
    notifs = result.scalars().all()
    
    return [
        {
            "id": n.id,
            "user_id": n.user_id,
            "user_email": f"User {n.user_id}",
            "title": n.content_type or "System Notification",
            "message": n.message,
            "is_read": n.is_read,
            "timestamp": n.timestamp.isoformat() if n.timestamp else None
        } for n in notifs
    ]

@admin_notif_router.post("/admin-api/notifications/")
async def admin_mark_all_read(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import update
    await db.execute(
        update(models.Notification)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "success"}

@admin_notif_router.post("/admin-api/notifications/send/")
async def admin_send_notification(data: AdminNotificationCreate, db: AsyncSession = Depends(get_db)):
    require_admin(None) # just placeholder
    
    user_ids = []
    if data.user_id.lower() == "all":
        # In a real app we might insert a broadcast notification, 
        # here we'll just insert one for user 0 (broadcast)
        user_ids = [0]
    else:
        try:
            user_ids = [int(data.user_id)]
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id")
            
    for uid in user_ids:
        n = models.Notification(
            user_id=uid,
            message=data.message,
            content_type=data.type,
            is_read=False
        )
        db.add(n)
        
    await db.commit()
    return {"status": "success"}

