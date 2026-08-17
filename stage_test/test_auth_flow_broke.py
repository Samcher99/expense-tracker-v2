'''
from app.database.db_conn import SessionLocal
from app.database.db_users import User
from app.core.security import (
    get_password_hash,
    create_access_token,
    get_current_user,
    get_user_by_email,
)

db = SessionLocal()

# 第一部分：新增測試使用者（如果還不存在的話）
existing_user = get_user_by_email(db, "test@example.com")

if existing_user is None:
    new_test_user = User(email="test@example.com", hashed_password=get_password_hash("test123"))
    db.add(new_test_user)
    db.commit()
    print("新測試使用者id: ", new_test_user.id)
else:
    print("測試使用者已存在，id: ", existing_user.id)

# 第二部分：驗證 get_current_user 能不能找回這個使用者
token = create_access_token(data={"sub": "test@example.com"})
user = get_current_user(token, db)

print("驗證成功，使用者：", user.email, "id:", user.id)

db.close()
'''
