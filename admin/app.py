from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from admin.admin.admin import UserAdmin
from admin.admin.auth import AdminAuth
from database.confdb import SyncSessionLocal, sync_engine
from load_env import SECRET_KEY, BASE_URL


app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
admin = Admin(
    app,
    sync_engine,
    session_maker=SyncSessionLocal,
    authentication_backend=AdminAuth(secret_key=SECRET_KEY),
    title="Raspis RGGU Admin",
    base_url=BASE_URL,
)
admin.add_view(UserAdmin)
