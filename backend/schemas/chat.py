"""
Pydantic schemas for chat-related requests and responses.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User's question or message")
    selected_documents: list[str] = Field(default=[], description="List of document IDs to query")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="LLM-generated reply")


class UploadResponse(BaseModel):
    """Response model for document upload endpoint."""
    message: str = Field(..., description="Upload status message")
    files: list[str] = Field(..., description="List of uploaded file names")
