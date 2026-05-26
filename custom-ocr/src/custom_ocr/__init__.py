"""基于 RapidOCR 的本地离线 OCR 文字识别 MCP 服务"""

__version__ = "1.0.0"

from custom_ocr.server import mcp


def main():
    mcp.run()
