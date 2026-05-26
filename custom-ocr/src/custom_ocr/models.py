from enum import Enum
from pydantic import BaseModel, Field


class OutputFormat(str, Enum):
    TEXT = "text"
    DETAILED = "detailed"
    BOTH = "both"


class TextBlock(BaseModel):
    text: str = Field(description="识别的文字内容")
    confidence: float = Field(description="置信度，0-1 之间")
    bounding_box: list[list[int]] = Field(
        description="文字区域的四个顶点坐标 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]",
    )


class OcrResult(BaseModel):
    text: str = Field(description="所有识别文字拼接的纯文本")
    blocks: list[TextBlock] = Field(description="逐行识别结果，含位置和置信度")
    block_count: int = Field(description="识别的文字块数量")
