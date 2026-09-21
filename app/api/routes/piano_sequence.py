from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.piano_sequence import PianoSequence
from app.models.user import User
from app.schemas.piano_sequence import PianoSequenceCreate, PianoSequenceOut, PianoSequenceUpdate

router = APIRouter(prefix="/piano/sequences", tags=["piano"])


@router.get("", response_model=list[PianoSequenceOut])
def list_sequences(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(PianoSequence)
        .filter(PianoSequence.created_by_id == current_user.id)
        .order_by(PianoSequence.created_at.desc())
        .all()
    )


@router.post("", response_model=PianoSequenceOut, status_code=status.HTTP_201_CREATED)
def create_sequence(payload: PianoSequenceCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_sequence = PianoSequence(**payload.model_dump(), created_by_id=current_user.id)
    db.add(new_sequence)
    db.commit()
    db.refresh(new_sequence)
    return new_sequence


@router.put("/{sequence_id}", response_model=PianoSequenceOut)
def update_sequence(
    sequence_id: int,
    payload: PianoSequenceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stored = (
        db.query(PianoSequence)
        .filter(PianoSequence.id == sequence_id, PianoSequence.created_by_id == current_user.id)
        .first()
    )
    if not stored:
        raise HTTPException(status_code=404, detail="Sequence not found")
    stored.name = payload.name
    stored.sequence = payload.sequence
    db.commit()
    db.refresh(stored)
    return stored


@router.delete("/{sequence_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sequence(sequence_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    stored = (
        db.query(PianoSequence)
        .filter(PianoSequence.id == sequence_id, PianoSequence.created_by_id == current_user.id)
        .first()
    )
    if not stored:
        raise HTTPException(status_code=404, detail="Sequence not found")
    db.delete(stored)
    db.commit()
    return None
