"""数据模型定义"""

from enum import Enum
from pydantic import BaseModel, Field


class SearchDepth(str, Enum):
    """搜索深度枚举"""
    BASIC = "basic"
    ADVANCED = "advanced"


class SearchRequest(BaseModel):
    """搜索请求参数"""
    query: str = Field(..., min_length=2, description="搜索关键词")
    search_depth: SearchDepth = Field(
        default=SearchDepth.BASIC,
        description="搜索深度：basic（快速）或 advanced（深入，消耗更多额度）",
    )
    max_results: int = Field(
        default=5,
        ge=1,
        le=10,
        description="返回结果数量，1-10",
    )
    include_answer: bool = Field(default=True, description="是否包含 AI 摘要")


class SearchResultItem(BaseModel):
    """单条搜索结果"""
    title: str = ""
    url: str = ""
    content: str = ""
    score: float = 0.0


class SearchResponse(BaseModel):
    """搜索响应"""
    query: str = ""
    answer: str = ""
    results: list[SearchResultItem] = []
    response_time: float = 0.0


class ExtractRequest(BaseModel):
    """内容提取请求参数"""
    urls: list[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="要提取内容的 URL 列表，最多10个",
    )


class ExtractResultItem(BaseModel):
    """单条提取结果"""
    url: str = ""
    raw_content: str = ""


class ExtractResponse(BaseModel):
    """内容提取响应"""
    results: list[ExtractResultItem] = []
    failed_urls: list[str] = []