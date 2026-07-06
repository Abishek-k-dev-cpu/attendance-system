from pydantic import BaseModel, Field


class UploadSummaryResponse(BaseModel):
    updated: int = Field(description="Number of attendance records updated")
    added: int = Field(description="Number of new attendance records created")
    failed: int = Field(description="Number of rows that failed validation")
    errors: list[str] = Field(default_factory=list, description="Details for failed rows")
