from __future__ import annotations

from typing import BinaryIO

from httpx import AsyncClient

from backend.infrastructure.httpx.dto.silicon_flow import *


class SiliconFlowClient:

    def __init__(self, http_client: AsyncClient) -> None:
        self._http_client = http_client

    async def model_list(self, *, api_key: str, model_type: str | None = None, base_url: str,
                         sub_type: str | None = None) -> list[SiliconModelListResponse]:
        params: dict[str, str] = {}
        if sub_type:
            params["sub_type"] = sub_type
        if type:
            params["type"] = model_type
        response = await self._http_client.get(
            f"{base_url}/models",
            headers={"Authorization": f"Bearer {api_key}"},
            params=params,
        )
        model_list = []
        payload = response.json()
        for item in payload["data"]:
            model_list.append(SiliconModelListResponse.model_validate(item))
        return model_list

    async def file_list(self, *, purpose: str, api_key: str, base_url: str, ) -> list[SiliconFileResponse]:
        response = await self._http_client.get(
            f"{base_url}/files",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "purpose": purpose,
            },
        )
        file_list = []
        payload = response.json()
        for item in payload["data"]["data"]:
            file_list.append(SiliconFileResponse.model_validate(item))
        return file_list

    async def file_upload(self, *, api_key: str, base_url: str, file_name: str, file_stream: BinaryIO, purpose: str) -> \
            list[SiliconFileResponse]:
        response = await self._http_client.post(
            f"{base_url}/files",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"purpose": purpose},
            files={"file": (file_name, file_stream)},
        )
        file_list = []
        payload = response.json()
        for item in payload["data"]:
            file_list.append(SiliconFileResponse.model_validate(item))
        return file_list

    async def get_batch_tasks(self, api_key: str, base_url: str) -> SiliconFlowTaskBatchResponse:
        response = await self._http_client.get(
            f"{base_url}/batches",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        payload = response.json()
        return payload["data"]

    async def establish_tasks(self, api_key: str, base_url: str, silicon_flow_task: SiliconFlowTask) -> SiliconFlowTask:
        response = await self._http_client.post(
            f"{base_url}/batches",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "input_file_id": silicon_flow_task.input_file_id,
                "endpoint": silicon_flow_task.endpoint,
                "completion_window": silicon_flow_task.completion_window,
                "metadata": silicon_flow_task.metadata,
                "replace": silicon_flow_task.replace,
            }
        )
        return response.json()["data"]

    async def get_task_details(self, api_key: str, base_url: str, batch_id: str) -> SiliconFlowTask:
        response = await self._http_client.get(
            f"{base_url}/batches/{batch_id}",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return response.json()["data"]

    async def cancel_task(self, api_key: str, base_url: str, batch_id: str) -> SiliconFlowTask:
        response = await self._http_client.post(
            f"{base_url}/batches/{batch_id}/ cancel",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        return response.json()["data"]

    async def create_video_request(self, api_key: str, base_url: str,
                                   silicon_flow_video: SiliconFlowVideoRequest) -> str:
        response = await self._http_client.post(
            f"{base_url}/video/submit",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": silicon_flow_video.model,
                "prompt": silicon_flow_video.prompt,
                "duration": silicon_flow_video.duration,
                "resolution": silicon_flow_video.resolution,
                "ratio": silicon_flow_video.ratio,
            }
        )
        return response.json()["data"]

    async def get_video_link(self, api_key: str, base_url: str, request_id: str) -> SiliconFlowVideoResponse:
        response = await self._http_client.get(
            f"{base_url}/video/status",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"requestId": request_id},
        )
        return response.json()["data"]

    async def upload_audio_voice(self, api_key: str, base_url: str, file_name: str, file_stream: BinaryIO, model: str,
                                 custom_name: str, text: str | None) -> str:
        response = await self._http_client.post(
            f"{base_url}/uploads/audio/voice",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "file": (file_name, file_stream),
                "model": model,
                "customName": custom_name,
                "text": text,
            }
        )
        return response.json()["data"]

    async def create_text_to_voice(self, api_key: str, base_url: str, model: str, input_text: str, voice: str,
                                   response_format: str) -> str:
        response = await self._http_client.post(
            f"{base_url}/audio/speech",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "input": input_text,
                "voice": voice,
                "response_format": response_format,
            }
        )
        return response.json()["data"]

    async def get_reference_voice_list(self, api_key: str, base_url: str, ) -> list[SiliconFlowVoiceListResponse]:
        response = await self._http_client.get(
            f"{base_url}/audio/voice/list",
            headers={"Authorization": f"Bearer {api_key}"},
        )
        payload = response.json()["data"]["result"]
        silicon_flow_voice_list = []
        for item in payload:
            silicon_flow_voice = SiliconFlowVoiceListResponse(
                model=item["model"],
                custom_name=item["customName"],
                text=item["text"],
                uri=item["uri"],
            )
            silicon_flow_voice_list.append(silicon_flow_voice)
        return silicon_flow_voice_list

    async def delete_reference_voice(self, api_key: str, base_url: str, uri: str) -> str:
        response = await self._http_client.post(
            f"{base_url}/audio/voice/deletions",
            headers={"Authorization": f"Bearer {api_key}"},
            params={"uri": uri},
        )
        return response.json()["data"]

    async def create_voice_to_text(self, api_key: str, base_url: str, file_name: str, file_stream: BinaryIO,
                                   model: str) -> str:
        response = await self._http_client.post(
            f"{base_url}/audio/transcriptions",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "file": (file_name, file_stream),
                "model": model,
            }
        )
        return response.json()["data"]

    async def create_image_generate_request(self, api_key: str, base_url: str, model: str, prompt: str,
                                            image_size: str, num_inference_steps: int,
                                            guidance_scale: float) -> SiliconFlowImageResponse:
        response = await self._http_client.post(
            f"{base_url}/images/generations",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "prompt": prompt,
                "image_size": image_size,
                "num_inference_steps": num_inference_steps,
                "guidance_scale": guidance_scale,
            },
        )
        payload = response.json()["data"]
        silicon_flow_image = SiliconFlowImageResponse(
            images=payload["images"],
            timings=payload["timings"],
            seed=payload["seed"],
        )
        return silicon_flow_image

    async def create_chat_request_openai(self,api_key:str,base_url:str,model:str,messages:list[SiliconFlowMessage]) -> SiliconFlowChatResponse:
        response = await self._http_client.post(
            f"{base_url}/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "messages": messages,
            }
        )
        return response.json()["data"]

    async def create_chat_request_anthropic(self,api_key:str,base_url:str,model:str,messages:list[SiliconFlowMessage],max_tokens:int) -> SiliconFlowChatResponse:
        response = await self._http_client.post(
            f"{base_url}/messages",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
            }
        )
        return response.json()["data"]

    async def create_chat_request_type_safe(self,api_key:str,base_url:str,model:str,state:str,question:SiliconFlowQuestion) -> SiliconFlowChatResponse:
        response = await self._http_client.post(
            f"{base_url}/systemone",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "state": state,
                "question": question,
            }
        )
        return response.json()["data"]

    async def create_insertion_request(self,api_key:str,base_url:str,model:str,input_text:str) -> SiliconFlowChatResponse:
        response = await self._http_client.post(
            f"{base_url}/embeddings",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "input": input_text,
            }
        )
        return response.json()["data"]

    async def rerank(self,api_key:str,base_url:str,model:str,query:str,documents:list[str],return_documents:bool,top_n:int) -> SiliconFlowChatResponse:
        response = await self._http_client.post(
            f"{base_url}/reranker",
            headers={"Authorization": f"Bearer {api_key}"},
            params={
                "model": model,
                "query": query,
                "documents": documents,
                "return_documents": return_documents,
                "top_n": top_n
            }
        )
        return response.json()["data"]