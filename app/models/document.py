from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base

class Document(Base):

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key = True)


    filename: Mapped[str] = mapped_column(String(255), nullable = False)

    status: Mapped [str] = mapped_column(String(20), nullable = False, default = "pending")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    
