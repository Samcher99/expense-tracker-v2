from app.core.security import get_password_hash, verify_password

test_password = "test123"
hashed = get_password_hash(test_password)

print("雜湊結果：", hashed)
print("正確密碼驗證：", verify_password(test_password, hashed))
print("錯誤密碼驗證：", verify_password("wrong_password", hashed))