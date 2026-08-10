from pydantic import BaseModel, ConfigDict
from datetime import datetime

from app.database.db_transactions import TransactionType, NeedType

class TransactionCreate(BaseModel):
    amount: int
    type: TransactionType
    need_type: NeedType | None = None

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    amount: int
    type: TransactionType
    need_type: NeedType | None = None
    created_at: datetime