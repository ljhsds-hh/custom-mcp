"""基于 Tavily API 的企业级 MCP 联网搜索服务"""

__version__ = "1.0.0"

from custom_web_search.server import mcp


def main():
    mcp.run()