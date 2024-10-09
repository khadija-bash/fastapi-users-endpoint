from sqlalchemy import Column, String, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql.functions import now
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(Text, nullable=True)
    name = Column(Text, nullable=True)
    email = Column(Text, nullable=True)
    sms = Column(Text, nullable=True)
    created = Column(TIMESTAMP, default=now())
    lastseen = Column(TIMESTAMP, nullable=True)
