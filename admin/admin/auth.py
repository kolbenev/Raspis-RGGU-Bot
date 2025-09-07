from fastapi import Request
from starlette.authentication import AuthCredentials, SimpleUser
from sqladmin.authentication import AuthenticationBackend

from load_env import ADMIN_USER, ADMIN_PASSWORD


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        if form.get("username") != ADMIN_USER:
            return False
        if form.get("password", "") != ADMIN_PASSWORD:
            return False
        request.session["user"] = ADMIN_USER
        return True

    async def logout(self, request: Request) -> None:
        request.session.clear()

    async def authenticate(self, request: Request):
        user = request.session.get("user")
        if not user:
            return
        return AuthCredentials(["authenticated"]), SimpleUser(user)
