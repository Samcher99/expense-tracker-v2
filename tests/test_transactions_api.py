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

def test_read_one_transaction(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == transaction_id
    assert data["amount"] == 100
    assert data["type"] == "expense"

def test_read_one_transaction_not_found(client, auth_headers):
    response = client.get(
        f"/transactions/99999",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "找不到要查詢的資料"

def test_read_one_transaction_forbidden(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    client.post(
        "/users",
        json={"email": "other_user@example.com", "password": "test123"},
    )
    login_response = client.post(
        "/token",
        data={"username": "other_user@example.com", "password": "test123"},
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    response = client.get(
        f"/transactions/{transaction_id}",
        headers=other_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "你沒有權限瀏覽這筆資料"

def test_delete_transaction(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/transactions/{transaction_id}",
        headers=auth_headers,
    )

    assert delete_response.status_code == 200
    assert delete_response.json() == {"ok": True}

    # 再查一次，確認真的被刪除了
    get_response = client.get(
        f"/transactions/{transaction_id}",
        headers=auth_headers,
    )
    assert get_response.status_code == 404


def test_delete_transaction_forbidden(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    client.post(
        "/users",
        json={"email": "other_user@example.com", "password": "test123"},
    )
    login_response = client.post(
        "/token",
        data={"username": "other_user@example.com", "password": "test123"},
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    delete_response = client.delete(
        f"/transactions/{transaction_id}",
        headers=other_headers,
    )

    assert delete_response.status_code == 403
    assert delete_response.json()["detail"] == "你沒有權限刪除這筆資料"


def test_update_transaction(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    update_response = client.patch(
        f"/transactions/{transaction_id}",
        json={"amount": 200},
        headers=auth_headers,
    )

    assert update_response.status_code == 200
    data = update_response.json()
    assert data["amount"] == 200
    assert data["type"] == "expense"
    assert data["need_type"] == "need"

def test_update_transaction_failed(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 200, "type": "income"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    update_response = client.patch(
        f"/transactions/{transaction_id}",
        json={"type": "expense"},
        headers=auth_headers,
    )
    assert update_response.status_code == 422
    assert update_response.json()["detail"] == "支出(expense)必須有 need_type"

def test_update_transaction_forbidden(client, auth_headers):
    create_response = client.post(
        "/transactions",
        json={"amount": 100, "type": "expense", "need_type": "need"},
        headers=auth_headers,
    )
    transaction_id = create_response.json()["id"]

    client.post(
        "/users",
        json={"email": "other_user@example.com", "password": "test123"},
    )
    login_response = client.post(
        "/token",
        data={"username": "other_user@example.com", "password": "test123"},
    )
    other_token = login_response.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    update_response = client.patch(
        f"/transactions/{transaction_id}",
        json={"amount": 600},
        headers=other_headers,
    )

    assert update_response.status_code == 403
    assert update_response.json()["detail"] == "你沒有權限修改這筆資料"


        





