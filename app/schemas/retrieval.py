from pydantic import BaseModel


class RetrievalSearchRequest(BaseModel):
    query: str


class RetrievalSearchResponse(BaseModel):
    query: str
    results: list
    contexts: list[str]