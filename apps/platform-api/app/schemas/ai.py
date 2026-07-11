from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=10_000)
    system_instruction: str | None = None


class GenerateResponse(BaseModel):
    model: str
    content: str