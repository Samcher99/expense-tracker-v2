from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db_users import User
from app.database.db_conn import get_db
from app.database.db_transactions import Transactions
from app.schemas.transactions import TransactionCreate, TransactionResponse
from app.core.security import get_current_user


router = APIRouter()

@router.post("/transactions", response_model=TransactionResponse)
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_transaction = Transactions(
        amount=transaction.amount, 
        type=transaction.type, 
        need_type=transaction.need_type,
        user_id=current_user.id
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction