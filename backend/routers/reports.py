from fastapi import APIRouter

router = APIRouter()

@router.post("/generate")
async def generate_report():
    return {"status": "ok", "message": "Report generation coming soon"}