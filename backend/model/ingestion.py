from pydantic import BaseModel

class IngestResponse(BaseModel):
    status: str
    message: str
    user_id: str
