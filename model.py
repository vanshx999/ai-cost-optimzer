from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Float, func
from sqlalchemy.orm import Session, declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://localhost:5432/ai_costs"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class RequestLog(Base):
    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    model = Column(String, nullable=False, index=True)
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    cached = Column(Boolean, default=False)
    latency_ms = Column(Integer, nullable=True)


    def __repr__(self) -> str:
        return f"RequesLog(user='{self.user_id}', model='{self.model}', cost=${self.cost:.4f})"
    

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

print("Table Created.")
