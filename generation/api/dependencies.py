# api/dependencies.py
from fastapi import Depends, Header, HTTPException, status
from services.generation_pipeline import GenerationService

# Giả sử bạn cần token để gọi API
def get_api_key(x_api_key: str = Header(...)):
    if x_api_key != "my-secret-key":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return x_api_key

# Inject service vào route
def get_generation_service() -> GenerationService:
    return GenerationService()
