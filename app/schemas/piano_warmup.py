from datetime import datetime

from pydantic import BaseModel, Field


class PianoWarmupCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sequence: str = Field(min_length=1, max_length=2048)


class PianoWarmupUpdate(PianoWarmupCreate):
    pass


class PianoWarmupOut(PianoWarmupCreate):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
