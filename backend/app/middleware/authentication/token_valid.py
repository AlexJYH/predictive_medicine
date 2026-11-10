from typing import Protocol

from backend.common.identity.model.identity import IdentityContext


class InvalidTokenError(Exception):
    """Token 无效、过期或已撤销。"""


class TokenServiceUnavailableError(Exception):
    """Token 验证服务不可用。"""


class TokenVerifier(Protocol):
    async def verify_access_token(
        self,
        access_token: str,
    ) -> IdentityContext:
        """验证 Token，成功返回身份，失败抛出对应异常。"""
        ...