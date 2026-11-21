from enum import Enum
from typing import cast


class LLMVendor(str,Enum):
    SILICON_FLOW = ("silicon_flow","Silicon Flow")
    OPENROUTER = ("openrouter","OpenRouter")

    def __new__(cls,code: str, label: str) -> "LLMVendor":
        member = cast("LLMVendor",str.__new__(cls,code))
        member._value_ = code
        member.code = code
        member.label = label
        return member

    code: str
    label: str

class SiliconFlowModel(str,Enum):
    TEXT = ("text","Text")
    IMAGE = ("image","Image")
    AUDIO = ("audio","Audio")
    VIDEO = ("video","Video")

    def __new__(cls,code: str, label: str) -> "SiliconFlowModel":
        member = cast("SiliconFlowModel",str.__new__(cls,code))
        member._value_ = code
        member.code = code
        member.label = label
        return member

    code: str
    label: str