"""MCP 服务定义"""

from mcp.server.fastmcp import FastMCP

from custom_ocr.engine import OcrEngine, OcrError, format_output
from custom_ocr.models import OutputFormat

mcp = FastMCP("custom-ocr")

_engine: OcrEngine | None = None


def _get_engine() -> OcrEngine:
    global _engine
    if _engine is None:
        _engine = OcrEngine()
    return _engine


@mcp.tool()
def ocr_image(
    image_path: str,
    output_format: str = "both",
) -> str:
    """识别本地图片中的文字内容。支持中英文混合识别，返回文字内容和位置信息。

    Args:
        image_path: 图片的本地文件路径，支持 jpg/png/bmp/webp/tiff 格式
        output_format: 输出格式 - text(纯文本), detailed(含位置信息), both(两者都返回)，默认 both
    """
    try:
        fmt = OutputFormat(output_format)
    except ValueError:
        return "错误：output_format 参数无效，可选值: text, detailed, both"

    engine = _get_engine()

    try:
        result = engine.recognize(image_path)
    except OcrError as e:
        return f"错误：{e}"
    except Exception as e:
        return f"错误：OCR 识别过程发生异常: {e}"

    return format_output(result, fmt)


@mcp.tool()
async def ocr_image_url(
    image_url: str,
    output_format: str = "both",
) -> str:
    """识别网络图片中的文字内容。下载图片后进行本地 OCR 识别，支持中英文混合。

    Args:
        image_url: 图片的 URL 地址
        output_format: 输出格式 - text(纯文本), detailed(含位置信息), both(两者都返回)，默认 both
    """
    try:
        fmt = OutputFormat(output_format)
    except ValueError:
        return "错误：output_format 参数无效，可选值: text, detailed, both"

    engine = _get_engine()

    try:
        result = await engine.recognize_url(image_url)
    except OcrError as e:
        return f"错误：{e}"
    except Exception as e:
        return f"错误：OCR 识别过程发生异常: {e}"

    return format_output(result, fmt)


@mcp.prompt()
def ocr_analysis_guide() -> str:
    """OCR 文字识别分析指南"""
    return """你是一个 OCR 文字识别助手。使用 ocr_image 或 ocr_image_url 工具识别图片中的文字。

使用建议：
1. 本地图片使用 ocr_image，网络图片使用 ocr_image_url
2. 如果只需要纯文本，设置 output_format 为 "text"
3. 如果需要了解文字在图片中的位置，设置 output_format 为 "detailed" 或 "both"
4. 默认支持中英文混合识别
5. 识别结果包含每行文字的置信度，置信度低于 0.5 的结果可能不准确"""


@mcp.resource("ocr://config")
def get_config() -> str:
    """获取当前 OCR 服务配置信息"""
    import custom_ocr

    return f"""custom-ocr 配置信息
版本: {custom_ocr.__version__}
引擎: RapidOCR (ONNX Runtime)
模式: 本地离线识别
支持格式: jpg, jpeg, png, bmp, webp, tiff
默认语言: 中英文混合"""
