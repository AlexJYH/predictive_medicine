from __future__ import annotations

from _contextvars import ContextVar, Token
from contextlib import contextmanager
from typing import Iterator

from backend.common.identity.model.identity import IdentityContext

_identity_context: ContextVar[IdentityContext] = ContextVar("identity_context")


def get_identity() -> IdentityContext:
    return _identity_context.get()


def require_identity() -> IdentityContext:
    identity = get_identity()
    return identity


def set_identity(identity: IdentityContext) -> Token[IdentityContext]:
    return _identity_context.set(identity)


def reset_identity(token: Token[IdentityContext]) -> None:
    _identity_context.reset(token)


@contextmanager
def identity_scope(identity: IdentityContext) -> Iterator[None]:
    token = set_identity(identity)
    try:
        yield
    finally:
        reset_identity(token)
