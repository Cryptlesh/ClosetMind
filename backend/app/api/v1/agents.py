from fastapi import APIRouter, Body
from ...services.coordinator import execute_outfit_planning

router = APIRouter()

@router.post("/plan-outfits")
async def plan_outfits(user_input: dict = Body(..., example={"prompt": "Pack for my weekend trip to Paris"})):
    """
    Orchestrates the POST /api/v1/agents/plan-outfits pipeline.
    Uses ADK SequentialAgent chaining Calendar -> Weather -> ParallelAgent(Stylist+Tips) -> Gemini VTON Tool
    """
    prompt = user_input.get("prompt", "")
    user_id = user_input.get("user_id", "default_usr_123")
    
    result_payload = await execute_outfit_planning(user_id, prompt)
    
    return {
        "status": "success",
        "data": result_payload
    }
