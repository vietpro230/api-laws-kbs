from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json

from api.dependencies import get_api_key, get_generation_service
from services.generation_pipeline import GenerationService
from models.schemas import GenerationRequest, GenerationResponse

router = APIRouter(
    prefix="/api/v1/generation",
    tags=["generation"],
    # dependencies=[Depends(get_api_key)]
)

@router.post("/generate")
def generate(
    body: GenerationRequest,
    service: GenerationService = Depends(get_generation_service)
) -> GenerationResponse:
    try:
        result = service.generate(body.query, body.custom_prompt)
        return GenerationResponse(
            result = result.get('answer', 'No response generated'),
            status = result.get('status', 'error')
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/generate/stream")
async def generate_stream(
    body: GenerationRequest,
    service: GenerationService = Depends(get_generation_service)
):
    async def event_generator():
        try:
            result = service.generate_stream(body.query, body.custom_prompt)

            for chunk in result:
                data = json.dumps({
                    "content": chunk,
                    "status": "streaming"
                }, ensure_ascii=False)
                yield f"data: {data}\n\n"

            yield f"data: {json.dumps({'status': 'completed'})}\n\n"

        except Exception as e:
            error_data = json.dumps({
                "error": str(e),
                "status": "error"
            }, ensure_ascii=False)
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.get("/")
def health_check():
    return {"status": "healthy"}