# custom-ocr

基于 [RapidOCR](https://github.com/RapidAI/RapidOCR) 的本地离线 OCR 文字识别 MCP 服务。

> **纯本地运行**：无需 API Key，无需联网，所有识别在本地完成，数据不出本机。

## 功能

| 工具 | 说明 |
|------|------|
| `ocr_image` | 识别本地图片中的文字，返回文字内容和位置信息 |
| `ocr_image_url` | 识别网络图片中的文字（下载后本地识别） |

| Prompt | 说明 |
|--------|------|
| `ocr_analysis_guide` | OCR 识别使用指南 |

| Resource | 说明 |
|----------|------|
| `ocr://config` | 当前 OCR 服务配置信息 |

## 特性

- 纯本地离线运行，无需 API Key，数据不出本机
- 默认中英文混合识别
- 返回文字内容 + 位置坐标 + 置信度
- 支持 jpg / png / bmp / webp / tiff 等常见图片格式
- 基于 ONNX Runtime 推理，无需 GPU，CPU 即可运行

## 快速开始

**第一步**：克隆仓库

```bash
git clone https://github.com/ljhsds-hh/custom-mcp.git
```

> **国内用户提示**：GitHub 访问可能需要网络代理

**第二步**：在 IDE 的 MCP 配置中添加（将路径替换为你的实际克隆路径）：

```json
{
  "mcpServers": {
    "custom-ocr": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-ocr",
        "run",
        "custom-ocr"
      ]
    }
  }
}
```

保存后重启 IDE 即可使用。

## 工具详情

### ocr_image

识别本地图片中的文字内容。

参数：
- `image_path`（必填）：图片的本地文件路径，支持 jpg/png/bmp/webp/tiff 格式
- `output_format`（可选）：输出格式，默认 `"both"`
  - `"text"` — 仅返回纯文本
  - `"detailed"` — 返回每行文字的位置坐标和置信度
  - `"both"` — 同时返回纯文本和详细信息

### ocr_image_url

识别网络图片中的文字（下载到本地临时文件后识别，识别完自动删除）。

参数：
- `image_url`（必填）：图片的 URL 地址
- `output_format`（可选）：同 ocr_image

## 各 IDE 配置指南

> 以下配置中的 `/你的路径/custom-mcp/custom-ocr` 替换为实际的克隆路径。

### Claude Code（默认）

在 `~/.claude/settings.json`（全局）或项目 `.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "custom-ocr": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-ocr",
        "run",
        "custom-ocr"
      ]
    }
  }
}
```

### Cursor

在 `~/.cursor/mcp.json`（全局）或项目 `.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "custom-ocr": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-ocr",
        "run",
        "custom-ocr"
      ]
    }
  }
}
```

### Trae

在 `~/.trae/mcp.json`（全局）或项目 `.trae/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "custom-ocr": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-ocr",
        "run",
        "custom-ocr"
      ]
    }
  }
}
```

### Windsurf

在 Windsurf Settings > Cascade > MCP Servers 中点击 "Add custom server"，或在 `mcp_config.json` 中添加：

```json
{
  "mcpServers": {
    "custom-ocr": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-ocr",
        "run",
        "custom-ocr"
      ]
    }
  }
}
```

添加后点击刷新按钮生效。

### VS Code (Roo Code / Cline)

在项目 `.roo/mcp.json` 或全局 MCP 配置中添加：

```json
{
  "mcpServers": {
    "custom-ocr": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-ocr",
        "run",
        "custom-ocr"
      ]
    }
  }
}
```

### Codex CLI

在 `~/.codex/config.toml` 中添加：

```toml
[mcp_servers.custom-ocr]
command = "uv"
args = [
    "--directory",
    "/你的路径/custom-mcp/custom-ocr",
    "run",
    "custom-ocr",
]
```

> **注意**：Codex CLI 目前仅支持 STDIO 模式的 MCP 服务器。

## License

MIT