import os
from fastapi import FastAPI

from api.config import settings
from api.routers.auto import router as auth_router
from api.routers.users import router as users_router
from api.routers.wallet import router as wallets_router

os.makedirs("logs", exist_ok=True)

app = FastAPI(debug=settings.DEBUG)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(wallets_router)


