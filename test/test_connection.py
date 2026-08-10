from app.database.db_conn import SessionLocal   # 這裡要 import 對路徑
from sqlalchemy import text

dbtestconn = SessionLocal()                        # 生一個 session

result = dbtestconn.execute(text("SELECT 1"))             # 執行查詢

print(result)                      # 看結果

dbtestconn.close()                              # 關閉 session