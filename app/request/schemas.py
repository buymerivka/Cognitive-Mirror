from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class RequestSchema(BaseModel):
    input_data: str
