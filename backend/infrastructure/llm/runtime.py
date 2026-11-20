from __future__ import annotations

import asyncio
from typing import Mapping, Any, Sequence, AsyncIterator, cast

from langchain_core.messages import BaseMessage, AIMessage, AIMessageChunk
from langchain_core.runnables import RunnableConfig
from langchain_core.utils.aiter import aclosing
from langchain_litellm import ChatLiteLLMRouter
from litellm import Router

from backend.common.config.model.llm_local_params import LLMLocalParamsSettings
from backend.services.llm_model.model.llm_model import LLMModelInfoDTO, LLMModelDTO, LLMVendorDTO


class ModelRuntime:
    _ALLOWED_OPTIONS = frozenset(
        {
            "temperature",
            "top_p",
            "max_tokens",
            "stop",
            "seed",
            "response_format",
            "tools",
            "tool_choice",
            "parallel_tool_calls",
            "enable_thinking",
            "thinking_budget",
            "reasoning_effort",
        }
    )

    def __init__(
            self,
            *,
            llm_local_params_setting: LLMLocalParamsSettings,
    ) -> None:
        self._llm_local_params_setting = llm_local_params_setting.llm_configs
        self._validate_limits()
        self._clients: dict[tuple[int, int, int], ChatLiteLLMRouter] = {}

    def _validate_limits(self) -> None:
        settings = self._llm_local_params_setting
        positive_fields = (
            "first_timeout",
            "between_timeout",
            "max_stream_time",
        )
        for name in positive_fields:
            if getattr(settings, name) <= 0:
                raise Exception(f"{name} must exist")
        if settings.retry < 0:
            raise Exception("retry must exceeding zero")
        if settings.fallback_times < 0:
            raise Exception("fallback_times must exceeding zero")

    def _deployment(self, model:LLMModelDTO, vendor: LLMVendorDTO, model_name: str) -> dict[str, Any,]:
        return {
            "model_name": model_name,
            "litellm_params": {
                "model": model.model,
                "api_base": vendor.url,
                "api_key": vendor.api_key,
            },
        }

    def _get_client(self, *, llm_model_info_dto:LLMModelInfoDTO) -> ChatLiteLLMRouter:
        main: LLMModelDTO | None = None
        fallback: LLMModelDTO | None = None
        for model_info in llm_model_info_dto.llm_model_dtos:
            if model_info.id == llm_model_info_dto.model_route_dto.model_id:
                main = model_info
            elif model_info.id == llm_model_info_dto.model_route_dto.fallback_id:
                fallback = model_info
        if self._llm_local_params_setting.fallback_times == 0:
            fallback = None
        cache_key = (
            llm_model_info_dto.model_route_dto.id,
            main.id,
            fallback.id if fallback is not None else None,
        )
        cached = self._clients.get(cache_key)
        if cached is not None:
            return cached
        vendor_map = {}
        for vendor in llm_model_info_dto.llm_vendor_dtos:
            vendor_map[vendor.id] = vendor
        deployment = [self._deployment(model=main, vendor=vendor_map[main.vendor_id], model_name=main.model,)]
        fallbacks: list[dict[str, list[str]]] = [{main.model: []}]
        if fallback is not None:
            deployment.append(
                self._deployment(
                    model=fallback,
                    vendor=vendor_map[fallback.vendor_id],
                    model_name=fallback.model,
                )
            )
            fallbacks = [{main.model: [fallback.model]},{fallback.model: []}]
        router = Router(
            model_list=deployment,
            num_retries=self._llm_local_params_setting.retry,
            max_fallbacks=self._llm_local_params_setting.fallback_times,
            fallbacks=fallbacks,
            timeout=self._llm_local_params_setting.first_timeout,
            stream_timeout=self._llm_local_params_setting.max_stream_time,
            enable_mid_stream_fallback_continuation=False,
        )

        client = ChatLiteLLMRouter(
            router=router,
            model=main.model,
            max_retries=self._llm_local_params_setting.retry,
            cache=False,
        )
        self._clients[cache_key] = client
        return client

    @classmethod
    def _prepare_options(cls, options: Mapping[str, Any] | None) -> dict[str, Any]:
        result = dict(options or {})
        unsupported = result.keys() - cls._ALLOWED_OPTIONS
        if unsupported:
            names = ", ".join(sorted(unsupported))
            raise Exception(f"不允许覆盖这些调用参数：{names}")
        return result

    async def ainvoke(
            self,
            *,
            llm_model_info_dto: LLMModelInfoDTO,
            message: Sequence[BaseMessage],
            options: Mapping[str, Any] | None = None,
            config: RunnableConfig | None = None,
    ) -> AIMessage:
        if not message:
            raise ValueError("messages 不能为空")
        client = self._get_client(llm_model_info_dto=llm_model_info_dto)
        kwargs = self._prepare_options(options)

        try:
            async with asyncio.timeout(self._llm_local_params_setting.first_timeout):
                result = await client.ainvoke(
                    list(message),
                    config=config,
                    **kwargs,
                )
        except asyncio.TimeoutError:
            raise Exception("普通模型调用超时")
        return cast(AIMessage, result)

    async def astream(
            self,
            *,
            llm_model_info_dto: LLMModelInfoDTO,
            message: Sequence[BaseMessage],
            options: Mapping[str, Any] | None = None,
            config: RunnableConfig | None = None,
    ) -> AsyncIterator[AIMessageChunk]:
        if not message:
            raise ValueError("messages 不能为空")
        client = self._get_client(llm_model_info_dto=llm_model_info_dto)
        kwargs = self._prepare_options(options)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self._llm_local_params_setting.max_stream_time
        first = True
        stream = client.astream(
            list(message),
            config=config,
            **kwargs,
        )
        async with aclosing(stream):
            while True:
                remaining = deadline - loop.time()
                if remaining <= 0:
                    raise Exception("流式调用超过总时限")

                idle_limit = (
                    self._llm_local_params_setting.first_timeout
                    if first
                    else self._llm_local_params_setting.between_timeout
                )
                wait_seconds = min(float(idle_limit), remaining)

                try:
                    async with asyncio.timeout(wait_seconds):
                        chunk = await anext(stream)
                except StopAsyncIteration:
                    return
                except TimeoutError as exc:
                    raise Exception("流式调用等待片段超时") from exc

                first = False
                yield cast(AIMessageChunk, chunk)
