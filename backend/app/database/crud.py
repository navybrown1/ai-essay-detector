import hashlib
from sqlalchemy.orm import Session
from .models import ScanRecord


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save_scan(db: Session, record: ScanRecord) -> int:
    db.add(record)
    db.commit()
    db.refresh(record)
    return record.id


def get_scan(db: Session, scan_id: int) -> ScanRecord | None:
    return db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()


def get_recent_scans(db: Session, limit: int = 20) -> list[ScanRecord]:
    return (
        db.query(ScanRecord)
        .order_by(ScanRecord.created_at.desc())
        .limit(limit)
        .all()
    )


def get_scans_by_author(db: Session, author_id: str) -> list[ScanRecord]:
    return (
        db.query(ScanRecord)
        .filter(ScanRecord.author_id == author_id)
        .order_by(ScanRecord.created_at.desc())
        .all()
    )


def delete_scan(db: Session, scan_id: int) -> bool:
    record = db.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
    if record:
        db.delete(record)
        db.commit()
        return True
    return False
