from typing import TypeVar, Any, Generic

from pydantic import Field

from backend.common.model.contract_model import ContractModel
from backend.common.enums.result_code import ResultCode

T = TypeVar("T")


class Context(ContractModel):
    trace_id: str = ""

    # @classmethod
    # def current(cls) -> "Context":
    #     return cls(trace_id=IdentityContext.get_identity().trace_id)


class Pagination(ContractModel):
    page_num: int = 1
    page_size: int = 10
    total: int = 0


class Response(ContractModel, Generic[T]):
    code: int = ResultCode.SUCCESS
    # message: str = Field(default_factory=lambda: message_for_code(ResultCode.SUCCESS))
    message: str | None = None
    data: T | None = None
    error: Any | None = None
    page: Pagination | None = None
    context: Context | None = Field(default_factory=Context.current)

    @classmethod
    def ok(cls, data: T | None = None) -> "Response[T]":
        return cls(data=data)

    @classmethod
    def page_data(
            cls,
            data: T,
            *,
            total: int,
            page_num: int,
            page_size: int,
    ) -> "Response[T]":
        return cls(
            data=data,
            page=Pagination(
                total=total,
                page_num=page_num,
                page_size=page_size,
            )
        )

    @classmethod
    def fail(
            cls,
            *,
            code: int = ResultCode.FAILED,
            message: str | None = None,
            error: Any | None = None,
    ) -> "Response[None]":
        # message = message_from_code(code)
        return cls(code=code, message=message, error=error)

    def ok_status(self) -> bool:
        return self.code == ResultCode.SUCCESS
