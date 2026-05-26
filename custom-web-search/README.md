# custom-web-search

基于 [Tavily API](https://tavily.com/) 的企业级 MCP 联网搜索服务。

> ⚠️ **重要说明**：本服务仅支持 Tavily 搜索引擎，你需要拥有 [Tavily API Key](https://app.tavily.com/) 才能使用。不支持其他搜索引擎的 API Key。

## 功能

| 工具 | 说明 |
|------|------|
| `search_web` | 网页搜索，返回结构化结果 + AI 摘要 |
| `extract_content` | 从 URL 提取网页内容，支持批量（最多10个） |
| `search_and_extract` | 搜索 + 提取一体化，获取更完整的资料 |

| Prompt | 说明 |
|--------|------|
| `research_topic` | 深度研究模板，引导 LLM 多轮搜索 + 提取 |

| Resource | 说明 |
|----------|------|
| `search://config` | 当前搜索服务配置信息 |

## 快速开始

**第一步**：获取 [Tavily API Key](https://app.tavily.com/)（注册即送免费额度）

**第二步**：克隆仓库

```bash
git clone https://github.com/ljhsds-hh/custom-mcp.git
```

> **国内用户提示**：GitHub 访问可能需要网络代理

**第三步**：在 IDE 的 MCP 配置中添加（将路径替换为你的实际克隆路径）：

```json
{
  "mcpServers": {
    "custom-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-web-search",
        "run",
        "custom-web-search"
      ],
      "env": {
        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

> **注意**：请将 `/你的路径/custom-mcp/custom-web-search` 替换为实际的克隆路径，将 `tvly-xxxxxxxxxxxxxxxxxx` 替换为你的 Tavily API Key。仅支持 Tavily 的 API Key，其他搜索引擎的 Key 无法使用。

保存后重启 IDE 即可使用。

## 工具详情

### search_web

搜索网页并返回结构化结果。

参数：
- `query`（必填）：搜索关键词
- `search_depth`（可选）：`"basic"` 快速搜索 或 `"advanced"` 深入搜索（消耗更多额度），默认 `"basic"`
- `max_results`（可选）：返回结果数量，1-10，默认 5

### extract_content

从指定 URL 提取网页内容。

参数：
- `urls`（必填）：URL 列表，最多 10 个

### search_and_extract

搜索并自动提取排名靠前结果的详细内容。消耗较多 API 额度。

参数：
- `query`（必填）：搜索关键词
- `max_results`（可选）：结果数量，1-5，默认 3

## 各 IDE 配置指南

> 以下配置中的 `tvly-xxxxxxxxxxxxxxxxxx` 均需替换为你自己的 Tavily API Key，`/你的路径/custom-mcp/custom-web-search` 替换为实际的克隆路径。

### Claude Code（默认）

在 `~/.claude/settings.json`（全局）或项目 `.claude/settings.json` 中添加：

```json
{
  "mcpServers": {
    "custom-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-web-search",
        "run",
        "custom-web-search"
      ],
      "env": {
        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Cursor

在 `~/.cursor/mcp.json`（全局）或项目 `.cursor/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "custom-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-web-search",
        "run",
        "custom-web-search"
      ],
      "env": {
        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Trae

在 `~/.trae/mcp.json`（全局）或项目 `.trae/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "custom-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-web-search",
        "run",
        "custom-web-search"
      ],
      "env": {
        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Windsurf

在 Windsurf Settings > Cascade > MCP Servers 中点击 "Add custom server"，或在 `mcp_config.json` 中添加：

```json
{
  "mcpServers": {
    "custom-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-web-search",
        "run",
        "custom-web-search"
      ],
      "env": {
        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"
      }
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
    "custom-web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/你的路径/custom-mcp/custom-web-search",
        "run",
        "custom-web-search"
      ],
      "env": {
        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

### Codex CLI

在 `~/.codex/config.toml` 中添加：

```toml
[mcp_servers.custom-web-search]
command = "uv"
args = [
    "--directory",
    "/你的路径/custom-mcp/custom-web-search",
    "run",
    "custom-web-search",
]

[mcp_servers.custom-web-search.env]
TAVILY_API_KEY = "tvly-xxxxxxxxxxxxxxxxxx"
```

> **注意**：Codex CLI 目前仅支持 STDIO 模式的 MCP 服务器。

## 特性

- ✅ 异步连接池，复用 TCP 连接
- ✅ 网络错误自动重试（指数退避）
- ✅ 完善的错误处理（认证/限流/网络/服务端 → 友好中文提示）
- ✅ Pydantic 参数校验，类型安全
- ✅ MCP 生命周期管理
- ✅ API Key 通过环境变量注入，不硬编码

## License

MIT