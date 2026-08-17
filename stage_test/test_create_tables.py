from app.database.db_conn import Base, engine
from app.database.db_users import User
from app.database.db_transactions import Transactions

Base.metadata.create_all(engine)

print("資料表建立完成！")