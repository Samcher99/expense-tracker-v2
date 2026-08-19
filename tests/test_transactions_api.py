def test_create_transaction(client, auth_headers):
    response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == 100
    assert data["type"] == "expense"
    assert "id" in data
    assert "user_id" in data

def test_create_transaction_failed(client, auth_headers):
    response = client.post(
        "/transactions",
        json={"amount": 100, "type": "income", "need_type": "need"},
        headers=auth_headers,
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Value error, 收入(income)不應該填寫 need_type"

def test_read_transactions(client, auth_headers):
    # 先新增兩筆交易
    client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    client.post(
        "/transactions",
        json={"amount": 5000, "type": "income"},
        headers=auth_headers,
    )

    # 查詢列表
    response = client.get("/transactions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

from app.database.db_users import User
from app.database.db_transactions import Transactions, TransactionType
from datetime import datetime

def test_read_transactions_with_date_filter(client, auth_headers, db_session):
    # 先透過 auth_headers 已經註冊過的使用者，查出它的真實 id
    user = db_session.query(User).filter(User.email == "transaction_test@example.com").first()

    # 直接在資料庫塞一筆「很久以前」的交易
    old_transaction = Transactions(
        amount=100,
        type=TransactionType.expense,
        need_type=None,
        user_id=user.id,
        created_at=datetime(2020, 1, 1),
    )
    db_session.add(old_transaction)
    db_session.commit()

    # 用「最近的區間」查詢，這筆很久以前的交易不該出現
    response = client.get("/transactions?start_date=2026-01-01", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0