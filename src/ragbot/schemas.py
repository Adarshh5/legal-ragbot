
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict

class UserMessage(BaseModel):
    human: str = Field(..., description="User input message, max 5 lines allowed")

    @validator('human')
    def max_five_lines(cls, value):
        line_count = value.count('\n') + 1
        if line_count > 5:
            raise ValueError('Only up to 5 lines are allowed in the input')
        return value

class ChatHistory(BaseModel):
    history :List[Dict]



class DeleteRequest(BaseModel):
    user_id: int
