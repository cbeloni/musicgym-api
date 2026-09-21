from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.piano_warmup import PianoWarmup
from app.models.user import User
from app.schemas.piano_warmup import PianoWarmupCreate, PianoWarmupOut, PianoWarmupUpdate

router = APIRouter(prefix="/piano/warmups", tags=["piano"])


@router.get("", response_model=list[PianoWarmupOut])
def list_warmups(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(PianoWarmup)
        .filter(PianoWarmup.created_by_id == current_user.id)
        .order_by(PianoWarmup.created_at.desc())
        .all()
    )


@router.post("", response_model=PianoWarmupOut, status_code=status.HTTP_201_CREATED)
def create_warmup(payload: PianoWarmupCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    warmup = PianoWarmup(**payload.model_dump(), created_by_id=current_user.id)
    db.add(warmup)
    db.commit()
    db.refresh(warmup)
    return warmup


@router.put("/{warmup_id}", response_model=PianoWarmupOut)
def update_warmup(
    warmup_id: int,
    payload: PianoWarmupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    warmup = (
        db.query(PianoWarmup)
        .filter(PianoWarmup.id == warmup_id, PianoWarmup.created_by_id == current_user.id)
        .first()
    )
    if not warmup:
        raise HTTPException(status_code=404, detail="Warmup not found")
    warmup.name = payload.name
    warmup.sequence = payload.sequence
    db.commit()
    db.refresh(warmup)
    return warmup


@router.delete("/{warmup_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_warmup(warmup_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    warmup = (
        db.query(PianoWarmup)
        .filter(PianoWarmup.id == warmup_id, PianoWarmup.created_by_id == current_user.id)
        .first()
    )
    if not warmup:
        raise HTTPException(status_code=404, detail="Warmup not found")
    db.delete(warmup)
    db.commit()
    return None
