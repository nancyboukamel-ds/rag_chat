from pydantic import BaseModel,Field
from enum import Enum
from datetime import datetime

class ModelName(str,Enum):
    GEMINI_1_5_FLASH = "gemini-2.5-flash"

class QueryInput(BaseModel):
    question:str
    session_id:str = Field(default=None)
    model: ModelName = Field(default=ModelName.GEMINI_1_5_FLASH)

class QueryResponse(BaseModel):
    answer:str
    session_id:str
    model:ModelName