from fastapi import APIRouter, UploadFile, File
from typing import List
from app.services.coordinator import process_vision_batch
from app.services.storage import storage_service
from app.core.settings import settings
import psycopg2
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/upload")
async def upload_wardrobe_items(files: List[UploadFile] = File(...)):
    """
    Ingests wardrobe images.
    Uses an ADK ParallelAgent to concurrently trigger zero-shot detection,
    extract tags, and explicitly saves them to AlloyDB.
    """
    
    # Save files via the unified StorageService
    saved_urls = []
    for file in files:
        url = await storage_service.save_file(file)
        saved_urls.append(url)
    
    # Pass to the service coordinator that orchestrates the ParallelAgent
    results = await process_vision_batch(saved_urls)
    
    # Save to AlloyDB
    if settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL:
        try:
            conn = psycopg2.connect(settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL)
            cur = conn.cursor()
            
            # Look up a valid user_id to satisfy foreign constraints
            cur.execute("SELECT id FROM users LIMIT 1;")
            user_row = cur.fetchone()
            if not user_row:
                # Fallback user if users table is empty
                cur.execute("INSERT INTO users (name) VALUES ('Test User') RETURNING id;")
                user_id = cur.fetchone()[0]
            else:
                user_id = user_row[0]
                
            for item in results:
                cur.execute("""
                    INSERT INTO wardrobe (user_id, category, color, material, tags, image_url)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    user_id, 
                    item.get("category", "Top"), 
                    item.get("color", "Unknown"), 
                    item.get("material", "Unknown"),
                    item.get("tags", []), 
                    item.get("filename")
                ))
            
            conn.commit()
            cur.close()
            conn.close()
            logger.info("Wardrobe items persistent in AlloyDB")
        except Exception as e:
            logger.error(f"AlloyDB Wardrobe Persistence Error: {e}")
            
    return {
        "status": "success",
        "processed_count": len(results),
        "data": results
    }

@router.get("/")
async def get_wardrobe_items():
    """
    Fetches the wardrobe items from AlloyDB.
    """
    if not settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL:
        return {"status": "error", "message": "Database not configured", "data": []}
        
    try:
        conn = psycopg2.connect(settings.MCP_TOOLBOX_AlloyDB_POSTGRES_URL)
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, image_url, category, color, material, tags 
            FROM wardrobe 
            ORDER BY created_at DESC;
        """)
        
        items = []
        for row in cur.fetchall():
            items.append({
                "id": row[0],
                "image": row[1],
                "category": row[2],
                "color": row[3],
                "material": row[4],
                "tags": row[5] or []
            })
            
        cur.close()
        conn.close()
        
        return {
            "status": "success",
            "data": items
        }
    except Exception as e:
        logger.error(f"AlloyDB Wardrobe Retrieval Error: {e}")
        return {"status": "error", "message": str(e), "data": []}
