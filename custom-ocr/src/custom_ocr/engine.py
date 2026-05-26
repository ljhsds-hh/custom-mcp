"""OCR 引擎封装"""

import os
import tempfile
from pathlib import Path
from urllib.parse import urlparse

import httpx
from rapidocr_onnxruntime import RapidOCR

from custom_ocr.models import OcrResult, TextBlock, OutputFormat


class OcrError(Exception):
    """OCR 基础异常"""


class OcrFileError(OcrError):
    """文件相关错误"""


class OcrDownloadError(OcrError):
    """下载相关错误"""


class OcrEngine:
    def __init__(self):
        self._engine: RapidOCR | None = None

    def _ensure_engine(self) -> RapidOCR:
        if self._engine is None:
            self._engine = RapidOCR()
        return self._engine

    def recognize(self, image_path: str) -> OcrResult:
        path = Path(image_path)

        if not path.exists():
            raise OcrFileError(f"文件不存在: {image_path}")

        if not path.is_file():
            raise OcrFileError(f"路径不是文件: {image_path}")

        supported = {".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"}
        if path.suffix.lower() not in supported:
            raise OcrFileError(
                f"不支持的图片格式: {path.suffix}，支持: {', '.join(sorted(supported))}"
            )

        engine = self._ensure_engine()

        try:
            result, _ = engine(str(path))
        except Exception as e:
            raise OcrError(f"OCR 识别失败: {e}") from e

        if not result:
            return OcrResult(text="", blocks=[], block_count=0)

        blocks = []
        text_parts = []
        for item in result:
            bbox_raw, text, confidence = item
            bbox = [
                [int(point[0]), int(point[1])]
                for point in bbox_raw
            ]
            blocks.append(
                TextBlock(
                    text=text,
                    confidence=round(confidence, 4),
                    bounding_box=bbox,
                )
            )
            text_parts.append(text)

        return OcrResult(
            text="\n".join(text_parts),
            blocks=blocks,
            block_count=len(blocks),
        )

    async def recognize_url(self, image_url: str) -> OcrResult:
        suffix = _guess_suffix_from_url(image_url)
        tmp_dir = tempfile.gettempdir()
        tmp_path = os.path.join(tmp_dir, f"custom_ocr_download{suffix}")

        try:
            async with httpx.AsyncClient(
                timeout=30.0, follow_redirects=True
            ) as client:
                try:
                    resp = await client.get(image_url)
                    resp.raise_for_status()
                except httpx.HTTPStatusError as e:
                    raise OcrDownloadError(
                        f"下载失败，HTTP {e.response.status_code}: {image_url}"
                    )
                except httpx.RequestError as e:
                    raise OcrDownloadError(f"下载失败，网络错误: {e}")

                content_type = resp.headers.get("content-type", "")
                if "image" not in content_type and not suffix:
                    raise OcrDownloadError(
                        f"URL 返回非图片内容: {content_type}"
                    )

                with open(tmp_path, "wb") as f:
                    f.write(resp.content)

            return self.recognize(tmp_path)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


def format_output(result: OcrResult, output_format: OutputFormat) -> str:
    if result.block_count == 0:
        return "未识别到文字内容"

    if output_format == OutputFormat.TEXT:
        return result.text

    if output_format == OutputFormat.DETAILED:
        lines = []
        for i, block in enumerate(result.blocks, 1):
            coords = ", ".join(f"({p[0]},{p[1]})" for p in block.bounding_box)
            lines.append(
                f"[{i}] {block.text}  (置信度: {block.confidence:.2%}, 位置: [{coords}])"
            )
        return "\n".join(lines)

    # BOTH
    lines = [result.text, "", "--- 详细信息 ---"]
    for i, block in enumerate(result.blocks, 1):
        coords = ", ".join(f"({p[0]},{p[1]})" for p in block.bounding_box)
        lines.append(
            f"[{i}] {block.text}  (置信度: {block.confidence:.2%}, 位置: [{coords}])"
        )
    return "\n".join(lines)


def _guess_suffix_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for ext in (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tiff", ".tif"):
        if path.endswith(ext):
            return ext
    return ".png"