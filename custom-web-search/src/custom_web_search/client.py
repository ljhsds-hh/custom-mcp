"""Tavily API 客户端 — 带重试、超时、错误处理"""

import asyncio
from typing import Any

import httpx

from .config import config
from .models import (
    SearchRequest,
    SearchResponse,
    SearchResultItem,
    ExtractRequest,
    ExtractResponse,
    ExtractResultItem,
)


class TavilyError(Exception):
    """Tavily API 基础异常"""
    pass


class TavilyAuthError(TavilyError):
    """认证异常 — API Key 无效或过期"""
    pass


class TavilyRateLimitError(TavilyError):
    """限流异常 — 调用额度已耗尽"""
    pass


class TavilyClient:
    """Tavily API 异步客户端

    特性：
    - 异步连接池，复用 TCP 连接
    - 网络错误自动重试（指数退避）
    - 完善的错误分类（认证/限流/网络/服务端）
    - 生命周期管理（配合 MCP lifespan）
    """

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    async def start(self) -> None:
        """创建异步 HTTP 客户端"""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=config.connect_timeout,
                read=config.read_timeout,
                write=10.0,
                pool=10.0,
            ),
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    async def close(self) -> None:
        """关闭客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _ensure_client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("TavilyClient 未初始化，请先调用 start()")
        return self._client

    async def _request_with_retry(self, url: str, payload: dict[str, Any]) -> dict[str, Any]:
        """带重试的 API 请求

        网络错误和 5xx 服务端错误会重试，业务错误（认证/限流）不重试。
        """
        client = self._ensure_client()
        last_error: Exception | None = None

        for attempt in range(config.max_retries):
            try:
                response = await client.post(url, json=payload)

                if response.status_code == 429:
                    raise TavilyRateLimitError("Tavily API 调用已达限额，请稍后重试")

                if response.status_code == 401:
                    raise TavilyAuthError("Tavily API Key 无效或已过期，请检查配置中的 TAVILY_API_KEY")

                response.raise_for_status()
                return response.json()

            except (TavilyAuthError, TavilyRateLimitError):
                raise  # 业务错误不重试
            except httpx.TimeoutException as e:
                last_error = e
                if attempt < config.max_retries - 1:
                    await asyncio.sleep(config.retry_backoff_factor * (2 ** attempt))
            except httpx.HTTPStatusError as e:
                if e.response.status_code >= 500 and attempt < config.max_retries - 1:
                    last_error = e
                    await asyncio.sleep(config.retry_backoff_factor * (2 ** attempt))
                else:
                    raise TavilyError(f"Tavily API 请求失败（HTTP {e.response.status_code}）") from e
            except httpx.HTTPError as e:
                last_error = e
                if attempt < config.max_retries - 1:
                    await asyncio.sleep(config.retry_backoff_factor * (2 ** attempt))
                else:
                    raise TavilyError(f"网络请求失败：{e}") from e

        raise TavilyError(f"请求重试 {config.max_retries} 次后仍失败：{last_error}") from last_error

    async def search(self, request: SearchRequest) -> SearchResponse:
        """执行网页搜索"""
        payload = {
            "api_key": config.tavily_api_key,
            "query": request.query,
            "search_depth": request.search_depth.value,
            "max_results": request.max_results,
            "include_answer": request.include_answer,
        }

        data = await self._request_with_retry(config.tavily_search_url, payload)

        return SearchResponse(
            query=request.query,
            answer=data.get("answer", ""),
            results=[
                SearchResultItem(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    content=item.get("content", ""),
                    score=item.get("score", 0.0),
                )
                for item in data.get("results", [])
            ],
            response_time=data.get("response_time", 0.0),
        )

    async def extract(self, request: ExtractRequest) -> ExtractResponse:
        """从 URL 提取网页内容"""
        payload = {
            "api_key": config.tavily_api_key,
            "urls": request.urls,
        }

        data = await self._request_with_retry(config.tavily_extract_url, payload)

        results = []
        failed = []
        for item in data.get("results", []):
            if item.get("raw_content"):
                results.append(ExtractResultItem(
                    url=item.get("url", ""),
                    raw_content=item.get("raw_content", ""),
                ))
            else:
                failed.append(item.get("url", ""))

        failed.extend(data.get("failed_urls", []))

        return ExtractResponse(results=results, failed_urls=failed)