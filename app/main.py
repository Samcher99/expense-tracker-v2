from fastapi import FastAPI

from app.api.users import router as users_router

from app.api.transactions import router as transactions_router

app = FastAPI(
    title="Expense Tracker API",
    description="個人記帳應用程式的後端 API",
    version="0.1.0",
)

app.include_router(users_router, tags=["Users"])
app.include_router(transactions_router, tags=["Transactions"])
