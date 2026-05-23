import datetime
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, JSON, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class ScanRecord(Base):
    __tablename__ = "scan_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String(255), default="pasted_text")
    essay_title = Column(String(255), default="Untitled")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    ai_score = Column(Float)
    human_score = Column(Float)
    mixed_score = Column(Float)
    confidence = Column(String(20))

    category_scores = Column(JSON)
    highlighted_sections = Column(JSON)
    sentence_scores = Column(JSON)
    paragraph_scores = Column(JSON)
    full_report = Column(JSON)

    text_hash = Column(String(64), index=True)
    word_count = Column(Integer)
    author_id = Column(String(64), nullable=True, index=True)


def init_db(db_url: str):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
