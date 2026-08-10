from app.core.security import create_access_token

token = create_access_token(data={"sub": "test@example.com"})
print("產生的 token：", token)