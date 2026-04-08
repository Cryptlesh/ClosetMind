from fastapi import APIRouter, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from app.services.storage import storage_service
from app.core.settings import settings
import logging
import psycopg2
logger = logging.getLogger(__name__)
router = APIRouter()

class ProfileResponse(BaseModel):
    status: str
    message: str
    data: dict

@router.post("/profile")
async def update_profile(
    name: str = Form(...),
    gender: str = Form(...),
    country: str = Form(...),
    state: str = Form(...),
    city: str = Form(...),
    selfie: Optional[UploadFile] = File(None)
):
    """
    Syncs the user profile and optional selfie from the ProfileEngine UI.
    """
    # 1. Process Selfie via Storage Service
    selfie_url = None
    if selfie:
        selfie_url = await storage_service.save_file(selfie)
        logger.info(f"Selfie processed: {selfie_url}")

    # 2. Save to AlloyDB
    db_status = "unconfigured"
    if settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL:
        try:
            conn = psycopg2.connect(settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL)
            cur = conn.cursor()
            
            # Check if user already exists
            cur.execute("SELECT id, selfie_url FROM users WHERE name = %s", (name,))
            existing = cur.fetchone()
            
            if existing:
                user_id = existing[0]
                final_selfie = selfie_url if selfie_url else existing[1]
                cur.execute("""
                    UPDATE users SET gender = %s, location = %s, selfie_url = %s 
                    WHERE id = %s RETURNING id;
                """, (gender, f"{city}, {state}, {country}", final_selfie, user_id))
            else:
                cur.execute("""
                    INSERT INTO users (name, gender, location, selfie_url)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                """, (name, gender, f"{city}, {state}, {country}", selfie_url))
                user_id = cur.fetchone()[0]
            conn.commit()
            cur.close()
            conn.close()
            db_status = "synced"
            logger.info(f"User {name} persistent in AlloyDB (ID: {user_id})")
        except Exception as e:
            logger.error(f"AlloyDB Persistence Error: {e}")
            db_status = f"error: {str(e)}"
    
    return {
        "status": "success",
        "message": "Neural Profile Synchronized",
        "database": db_status,
        "data": {
            "name": name,
            "gender": gender,
            "location": f"{city}, {state}, {country}",
            "selfie_url": selfie_url if selfie else None
        }
    }

@router.get("/profile", response_model=ProfileResponse)
async def get_profile():
    """
    Retrieves the latest user profile from AlloyDB.
    """
    if not settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL:
        return {
            "status": "error",
            "message": "Database not configured",
            "data": {}
        }
    
    try:
        conn = psycopg2.connect(settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL)
        cur = conn.cursor()
        
        # For hackathon, we just get the most recently created user
        cur.execute("""
            SELECT name, gender, location, selfie_url FROM users
            ORDER BY created_at DESC LIMIT 1;
        """)
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if row:
            name, gender, location, selfie_url = row
            # Location is stored as "city, state, country"
            loc_parts = location.split(", ")
            return {
                "status": "success",
                "message": "Profile Retrieved",
                "data": {
                    "name": name,
                    "gender": gender,
                    "location": location,
                    "city": loc_parts[0] if len(loc_parts) > 0 else "",
                    "state": loc_parts[1] if len(loc_parts) > 1 else "",
                    "country": loc_parts[2] if len(loc_parts) > 2 else "",
                    "selfie_url": selfie_url
                }
            }
        else:
            return {
                "status": "success",
                "message": "No profile found",
                "data": {}
            }
    except Exception as e:
        logger.error(f"AlloyDB Retrieval Error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "data": {}
        }
