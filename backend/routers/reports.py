from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from engines.report_generator import generate_pdf_report
import json

router = APIRouter()


@router.post("/generate")
async def generate_report(payload: dict):
    """
    Generates a PDF forensic report from analysis results.
    Expects the full analysis response object from /analyze/image, /analyze/audio, or /analyze/video.
    """
    try:
        analysis_result = payload.get("analysis_result", {})
        filename = payload.get("filename", "unknown")
        media_type = payload.get("media_type", "unknown")

        if not analysis_result:
            raise HTTPException(status_code=400, detail="No analysis result provided")

        pdf_bytes = generate_pdf_report(analysis_result, filename, media_type)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=blacklight_report_{filename}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")