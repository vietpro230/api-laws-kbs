from fastapi import APIRouter, Depends, HTTPException
from api.dependencies import get_api_key, get_generation_service
from services.generation_pipeline import GenerationService
from models.schemas import GenerationRequest, GenerationResponse

router = APIRouter(
    prefix="/api/v1/generation",
    tags=["generation"],
    dependencies=[Depends(get_api_key)]
)

@router.post("/generate")
def generate(
    body: GenerationRequest,
    service: GenerationService = Depends(get_generation_service)
) -> GenerationResponse:
    try:
        result = service.generate(body.query)
        return GenerationResponse(
            result=result.get('answer', 'No response generated'),
            status=result.get('status', 'error')
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/")
def health_check():
    return {"status": "healthy"}