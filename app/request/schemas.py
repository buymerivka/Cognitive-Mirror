from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class RequestSchema(BaseModel):
    input_data: str


class ResponseSchema(BaseModel):
    analyzed_data: list[dict]


class TotalResponseSchema(BaseModel):
    manipulations_analyzed: list[dict]
    emotions_analyzed: list[dict]
