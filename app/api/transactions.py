from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.db_users import User
from app.database.db_conn import get_db
from app.database.db_transactions import Transactions
from app.schemas.transactions import TransactionCreate, TransactionResponse, TransactionUpdate, TransactionType
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


@router.get("/transactions", response_model=list[TransactionResponse])
def read_transaction(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    history_transactions = select(Transactions).where(Transactions.user_id == current_user.id)
    result = db.execute(history_transactions)
    return result.scalars().all()

@router.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tbd_transaction = db.get(Transactions, transaction_id)
    if not tbd_transaction:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="找不到要刪除的資料"
        )
    if tbd_transaction.user_id != current_user.id:
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="你沒有權限刪除這筆交易",
        )
    db.delete(tbd_transaction)
    db.commit()
    return {"ok": True}

@router.patch("/transactions/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction: TransactionUpdate,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    tbu_transaction = db.get(Transactions, transaction_id)
    if not tbu_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="找不到要修改的資料"
        )

    if tbu_transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="你沒有權限刪除這筆資料"
        )
    transaction_data = transaction.model_dump(exclude_unset=True) 
    for key, value in transaction_data.items():                     
        setattr(tbu_transaction, key, value)

    # 合併後,檢查「更新完之後」的資料合不合理
    if tbu_transaction.type == TransactionType.income and tbu_transaction.need_type is not None:
        raise HTTPException(status_code=422, detail="收入(income)不應該有 need_type")
    if tbu_transaction.type == TransactionType.expense and tbu_transaction.need_type is None:
        raise HTTPException(status_code=422, detail="支出(expense)必須有 need_type")
    
    db.add(tbu_transaction)
    db.commit()
    db.refresh(tbu_transaction)
    return tbu_transaction