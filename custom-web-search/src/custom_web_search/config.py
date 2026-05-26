"""配置管理模块

API Key 通过 MCP 配置的 env 参数注入，不硬编码在代码中。
"""

import os


class Config:
    """MCP 服务配置"""

    # API Key — 由 MCP 配置中的 env 参数注入
    tavily_api_key: str = os.environ.get("TAVILY_API_KEY", "")

    # 搜索默认参数
    default_search_depth: str = "basic"
    default_max_results: int = 5

    # HTTP 客户端参数
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    max_retries: int = 3
    retry_backoff_factor: float = 0.5

    # Tavily API 地址
    tavily_search_url: str = "https://api.tavily.com/search"
    tavily_extract_url: str = "https://api.tavily.com/extract"

    def validate(self) -> None:
        """启动时校验配置，无效则抛出异常"""
        if not self.tavily_api_key:
            raise ValueError(
                "未设置 TAVILY_API_KEY。\n"
                "请在 MCP 配置中通过 env 参数设置：\n"
                '{\n'
                '  "mcpServers": {\n'
                '    "custom-web-search": {\n'
                '      "command": "uvx",\n'
                '      "args": ["custom-web-search"],\n'
                '      "env": {\n'
                '        "TAVILY_API_KEY": "tvly-xxxxxxxxxxxxxxxxxx"\n'
                '      }\n'
                '    }\n'
                '  }\n'
                '}'
            )
        if not self.tavily_api_key.startswith("tvly-"):
            raise ValueError(
                f"TAVILY_API_KEY 格式无效，应以 'tvly-' 开头。"
            )


config = Config()