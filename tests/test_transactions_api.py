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