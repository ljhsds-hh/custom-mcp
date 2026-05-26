"""MCP 服务定义 — Tools / Prompts / Resources"""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from mcp.server.fastmcp import FastMCP, Context

from .config import config
from .client import TavilyClient, TavilyError, TavilyAuthError, TavilyRateLimitError
from .models import SearchRequest, SearchDepth, ExtractRequest

# ──────────────────────────────────────
# 生命周期管理
# ──────────────────────────────────────

_client: TavilyClient | None = None


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[dict]:
    """MCP 服务生命周期：启动时校验配置、创建客户端，关闭时销毁"""
    global _client
    config.validate()
    _client = TavilyClient()
    await _client.start()
    try:
        yield {"client": _client}
    finally:
        await _client.close()
        _client = None


def _get_client() -> TavilyClient:
    """获取客户端实例"""
    if not _client:
        raise RuntimeError("搜索服务未就绪，请稍后重试")
    return _client


# ──────────────────────────────────────
# MCP 服务实例
# ──────────────────────────────────────

mcp = FastMCP(
    name="custom-web-search",
    lifespan=app_lifespan,
)


# ──────────────────────────────────────
# 格式化辅助函数
# ──────────────────────────────────────

def _format_search(query: str, answer: str, results: list, response_time: float) -> str:
    """格式化搜索结果"""
    parts: list[str] = []

    if answer:
        parts.append(f"## AI 摘要\n{answer}\n")

    parts.append(f"## 搜索结果（共 {len(results)} 条，耗时 {response_time:.2f}s）\n")

    for i, item in enumerate(results, 1):
        parts.append(f"### {i}. {item.title or '无标题'}")
        parts.append(f"🔗 {item.url}")
        parts.append(f"{item.content}\n")

    return "\n".join(parts)


def _format_extract(results: list, failed_urls: list[str]) -> str:
    """格式化提取结果"""
    parts: list[str] = []

    if results:
        parts.append(f"## 提取结果（共 {len(results)} 条）\n")
        for i, item in enumerate(results, 1):
            parts.append(f"### {i}. {item.url}")
            content = item.raw_content
            if len(content) > 3000:
                content = content[:3000] + "\n...(内容已截断)"
            parts.append(f"{content}\n")

    if failed_urls:
        parts.append("## 提取失败的链接\n")
        for url in failed_urls:
            parts.append(f"- {url}")

    return "\n".join(parts) if parts else "未提取到任何内容"


# ──────────────────────────────────────
# Tools
# ──────────────────────────────────────

@mcp.tool()
async def search_web(
    query: str,
    search_depth: str = "basic",
    max_results: int = 5,
) -> str:
    """使用 Tavily 搜索引擎搜索网页并返回结构化结果

    Args:
        query: 搜索关键词
        search_depth: 搜索深度，"basic"（快速）或 "advanced"（深入，消耗更多额度）
        max_results: 返回结果数量，1-10
    """
    try:
        depth = SearchDepth(search_depth)
    except ValueError:
        return f"❌ 参数错误：search_depth 只能是 'basic' 或 'advanced'，当前值：'{search_depth}'"

    if not 1 <= max_results <= 10:
        return f"❌ 参数错误：max_results 范围为 1-10，当前值：{max_results}"

    client = _get_client()

    try:
        request = SearchRequest(
            query=query,
            search_depth=depth,
            max_results=max_results,
        )
        response = await client.search(request)
    except TavilyAuthError as e:
        return f"❌ 认证失败：{e}"
    except TavilyRateLimitError as e:
        return f"❌ 调用限流：{e}"
    except TavilyError as e:
        return f"❌ 搜索服务异常：{e}"

    return _format_search(
        query=response.query,
        answer=response.answer,
        results=response.results,
        response_time=response.response_time,
    )


@mcp.tool()
async def extract_content(
    urls: list[str],
) -> str:
    """从指定 URL 提取网页内容，支持批量提取（最多10个URL）

    Args:
        urls: 要提取内容的 URL 列表，最多10个
    """
    if not urls:
        return "❌ 参数错误：urls 不能为空"
    if len(urls) > 10:
        return f"❌ 参数错误：最多支持 10 个 URL，当前提交了 {len(urls)} 个"

    client = _get_client()

    try:
        request = ExtractRequest(urls=urls)
        response = await client.extract(request)
    except TavilyAuthError as e:
        return f"❌ 认证失败：{e}"
    except TavilyRateLimitError as e:
        return f"❌ 调用限流：{e}"
    except TavilyError as e:
        return f"❌ 提取服务异常：{e}"

    return _format_extract(
        results=response.results,
        failed_urls=response.failed_urls,
    )


@mcp.tool()
async def search_and_extract(
    query: str,
    max_results: int = 3,
) -> str:
    """搜索网页并自动提取排名靠前结果的详细内容

    先执行搜索，再对搜索结果中的链接进行内容提取，返回更完整的资料。
    注意：此工具消耗较多 API 额度。

    Args:
        query: 搜索关键词
        max_results: 搜索并提取的结果数量，1-5（建议不超过3）
    """
    if not 1 <= max_results <= 5:
        return f"❌ 参数错误：max_results 范围为 1-5，当前值：{max_results}"

    client = _get_client()

    try:
        # 第一步：搜索
        search_response = await client.search(
            SearchRequest(
                query=query,
                search_depth=SearchDepth.BASIC,
                max_results=max_results,
                include_answer=True,
            )
        )

        # 第二步：提取搜索结果中的内容
        urls = [r.url for r in search_response.results if r.url]
        extract_response = None
        if urls:
            extract_response = await client.extract(ExtractRequest(urls=urls))

    except TavilyAuthError as e:
        return f"❌ 认证失败：{e}"
    except TavilyRateLimitError as e:
        return f"❌ 调用限流：{e}"
    except TavilyError as e:
        return f"❌ 服务异常：{e}"

    # 合并结果
    parts: list[str] = []
    if search_response.answer:
        parts.append(f"## AI 摘要\n{search_response.answer}\n")

    parts.append(f"## 搜索 + 提取结果（耗时 {search_response.response_time:.2f}s）\n")

    extracted_map: dict[str, str] = {}
    if extract_response:
        for item in extract_response.results:
            extracted_map[item.url] = item.raw_content

    for i, sr in enumerate(search_response.results, 1):
        parts.append(f"### {i}. {sr.title or '无标题'}")
        parts.append(f"🔗 {sr.url}")
        if sr.url in extracted_map:
            content = extracted_map[sr.url]
            if len(content) > 3000:
                content = content[:3000] + "\n...(内容已截断)"
            parts.append(f"**完整内容：**\n{content}\n")
        else:
            parts.append(f"{sr.content}\n")

    if extract_response and extract_response.failed_urls:
        parts.append("## 提取失败的链接\n")
        for url in extract_response.failed_urls:
            parts.append(f"- {url}")

    return "\n".join(parts)


# ──────────────────────────────────────
# Prompts
# ──────────────────────────────────────

@mcp.prompt()
def research_topic(topic: str) -> str:
    """深度研究某个主题的 Prompt 模板

    引导 LLM 多轮搜索 + 提取，产出结构化研究报告。

    Args:
        topic: 要研究的主题
    """
    return (
        f"请对以下主题进行深度研究：{topic}\n\n"
        "研究步骤：\n"
        "1. 使用 search_web 进行初步搜索，了解概览\n"
        "2. 根据初步结果，使用 search_web（search_depth=advanced）深入搜索关键子主题\n"
        "3. 对重要页面使用 extract_content 提取完整内容\n"
        "4. 综合所有信息，撰写结构化的研究报告\n\n"
        "报告要求：\n"
        "- 包含概述、关键发现、详细分析、结论\n"
        "- 标注信息来源\n"
        "- 指出信息空白和不确定性"
    )


# ──────────────────────────────────────
# Resources
# ──────────────────────────────────────

@mcp.resource("search://config")
def get_search_config() -> str:
    """获取当前搜索服务配置信息"""
    key_display = f"{config.tavily_api_key[:8]}...{config.tavily_api_key[-4:]}" if config.tavily_api_key else "未设置"
    return (
        "## 搜索服务配置\n"
        f"- 服务名称：custom-web-search\n"
        f"- 搜索引擎：Tavily\n"
        f"- 默认搜索深度：{config.default_search_depth}\n"
        f"- 默认结果数量：{config.default_max_results}\n"
        f"- 连接超时：{config.connect_timeout}s\n"
        f"- 读取超时：{config.read_timeout}s\n"
        f"- 最大重试次数：{config.max_retries}\n"
        f"- API Key：{key_display}\n"
    )