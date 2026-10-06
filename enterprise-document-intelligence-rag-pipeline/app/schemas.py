from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    directory: str = Field(default="data/documents")


class SearchRequest(BaseModel):
    query: str = Field(min_length=2)
    top_k: int = Field(default=5, ge=1, le=20)


class QueryRequest(SearchRequest):
    pass
