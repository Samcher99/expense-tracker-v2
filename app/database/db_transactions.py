from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import func
from sqlalchemy import ForeignKey

from datetime import datetime
from sqlalchemy import Enum

import enum

from app.database.db_conn import Base

class TransactionType(enum.Enum):
    income = "income"
    expense = "expense"

class NeedType(enum.Enum):
    need = "need"
    want = "want"

class Transactions(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column()
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType))
    need_type: Mapped[NeedType | None] = mapped_column(Enum(NeedType),nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())