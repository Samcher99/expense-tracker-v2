from pydantic import BaseModel, ConfigDict, model_validator, Field
from typing_extensions import Self
from datetime import datetime

from app.database.db_transactions import TransactionType, NeedType

class TransactionCreate(BaseModel):
    amount: int = Field(gt=0)
    type: TransactionType
    need_type: NeedType | None = None

    @model_validator(mode='after')
    def check_need_type_only_for_expense(self) -> Self:
        if self.type == TransactionType.income and self.need_type is not None:
            raise ValueError('收入(income)不應該填寫 need_type')
        if self.type == TransactionType.expense and self.need_type is None:
            raise ValueError('支出(expense)必須填寫need_type(need/want)')
        return self

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    amount: int
    type: TransactionType
    need_type: NeedType | None = None
    created_at: datetime

class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    need_type: NeedType | None = None
