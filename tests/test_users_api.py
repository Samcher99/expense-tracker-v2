def test_register_user(client):
    response = client.post(
        "/users",
        json={"email": "integration_test@example.com", "password": "test123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "integration_test@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_email(client):
    # 第一次註冊：應該成功
    client.post(
        "/users",
        json={"email": "duplicate@example.com", "password": "test123"},
    )

    # 第二次註冊，用同樣的 email：應該被擋下
    response = client.post(
        "/users",
        json={"email": "duplicate@example.com", "password": "test123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "這個信箱已經被註冊過了"

def test_password_is_hashed(client, db_session):
    client.post(
        "/users",
        json={"email": "hash_check@example.com", "password": "test123"},
    )

    from app.database.db_users import User
    user_in_db = db_session.query(User).filter(User.email == "hash_check@example.com").first()

    assert user_in_db.hashed_password != "test123"
    assert user_in_db.hashed_password.startswith("$argon2")

def test_login_success(client):
    # 先註冊一個使用者
    client.post(
        "/users",
        json={"email": "login_test@example.com", "password": "test123"},
    )

    # 用剛才註冊的帳密登入
    response = client.post(
        "/token",
        data={"username": "login_test@example.com", "password": "test123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failed(client):
    # 先註冊一個使用者
    client.post(
        "/users",
        json={"email": "login_test@example.com", "password": "test123"},
    )

    # 用剛才註冊的帳密登入
    response = client.post(
        "/token",
        data={"username": "login_test@example.com", "password": "wrongpassward"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "帳號或密碼錯誤"

def test_read_users_me(client):
    # 第一步：註冊
    client.post(
        "/users",
        json={"email": "me_test@example.com", "password": "test123"},
    )

    # 第二步：登入拿 token
    login_response = client.post(
        "/token",
        data={"username": "me_test@example.com", "password": "test123"},
    )
    token = login_response.json()["access_token"]

    # 第三步：帶著 token 呼叫 GET /users/me
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me_test@example.com"

def test_read_users_me_invalid_token(client):
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer this_is_not_a_valid_token"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token 無效或已過期"