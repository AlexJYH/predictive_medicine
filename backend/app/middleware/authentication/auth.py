from __future__ import annotations

import asyncio
from collections.abc import Collection

from starlette.datastructures import Headers
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from backend.app.middleware.authentication.token_valid import TokenVerifier, InvalidTokenError, \
    TokenServiceUnavailableError
from backend.common.enums.result_code import ResultCode
from backend.common.identity.context import reset_identity, set_identity
from backend.common.identity.model.identity import IdentityContext
from backend.services.identity.runtime import get_identity_service


class AuthenticationMiddleware:

    def __init__(self, app: ASGIApp, *, environment: str, public_routes: Collection[tuple[str, str]],
                 token_verifier: TokenVerifier | None = None, verification_timeout_seconds: float) -> None:
        self.app = app
        self._environment = environment
        self._public_routes = frozenset(
            (method.upper(), path)
            for method, path in public_routes
        )
        self._token_verifier = token_verifier
        self._verification_timeout_seconds = verification_timeout_seconds

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "websocket":
            await send({"type":"websocket.close", "code": ResultCode.COULD_NOT_ACCEPT_WEBSOCKET})
            return

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope["method"].upper()
        path = scope["path"]

        if (method, path) in self._public_routes:
            await self.app(scope, receive, send)
            return

        headers = Headers(scope = scope)

        credential_names = (
            "authorization",
            "x-tenant-id",
            "x-user-id",
        )

        for name in credential_names:
            if len(headers.getlist(name)) > 1:
                await self._reject(scope,receive, send, ResultCode.HEADER_MUST_BE_INDEPENDENT,"header must be independent")
                return

        authorization_valid = "authorization" in headers
        tenant_valid = "X-Tenant-Id" in headers or "X-User-Id" in headers

        if authorization_valid and tenant_valid:
            await self._reject(scope, receive, send, ResultCode.HEADER_MUST_BE_INDEPENDENT, "token and identity can't be used together")
            return

        identity = ()
        if self._environment == "dev":
            if authorization_valid:
                await self._reject(scope, receive, send, ResultCode.HEADER_VALID,"dev environment only accept identity header")
                return

            tenant_id = headers.get("X-Tenant-Id")
            user_id = headers.get("X-User-Id")
            identity = IdentityContext(tenant_id=int(tenant_id), user_id=int(user_id),)
            valid = await get_identity_service().validate_identity(identity)
            if not valid:
                await self._reject(scope, receive, send, ResultCode.HEADER_VALID,"invalid identity header")
                return
        else:
            if tenant_valid:
                await self._reject(scope, receive, send, ResultCode.HEADER_VALID,"this environment only accept bearer token")
                return

            authorization = headers.get("authorization")
            parts = authorization.split()

            if len(parts) != 2 or parts[0].lower() != "bearer":
                await self._reject(scope, receive, send, ResultCode.HEADER_VALID,"need valid bearer token" )
                return

            try:
                async with asyncio.timeout(self._verification_timeout_seconds):
                    identity = (await self._token_verifier.verify_access_token(parts[1]))
            except InvalidTokenError:
                await self._reject(scope,receive,send,ResultCode.HEADER_VALID,"invalid bearer token")
                return
            except (TokenServiceUnavailableError,TimeoutError):
                await self._reject(scope,receive,send,ResultCode.AUTHORIZATION_SERVICE_UNAVAILABLE,"authorization service is unavailable")
                return
            if identity.user_id <= 0 or identity.tenant_id <= 0:
                await self._reject(scope,receive,send,ResultCode.HEADER_VALID,"invalid bearer token")
                return

        context_token = set_identity(identity)
        try:
            await self.app(scope, receive, send)
        finally:
            reset_identity(context_token)


    @staticmethod
    async def _reject(scope: Scope, receive: Receive, send: Send, status_code:int,message:str) -> None:
        response = JSONResponse(
            status_code=status_code,
            content={"detail": message},
        )
        await response(scope, receive, send)