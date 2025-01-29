from pydantic import BaseModel
from typing import List, Optional

class DocumentSegment(BaseModel):
    text: str
    start_index: int
    end_index: int

class DocumentMetadata(BaseModel):
    id: str
    filename: str
    media_type: str

class DocumentResponse(BaseModel):
    metadata: DocumentMetadata
    segments: List[DocumentSegment]
    explanations: Optional[List[DocumentSegment]] = []

class AnalysisRequest(BaseModel):
    document_id: str
    text: str

class Citation(BaseModel):
    cited_text: str
    start_char_index: int
    end_char_index: int

class AnalysisResponse(BaseModel):
    content: str
    citations: List[dict] = []
