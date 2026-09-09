"""
rag/article_source.py

AutoSearch V7

RAG-1.1

Article Source

功能：

    透過 MCP Client 取得 AutoSearch Article。

資料流程：

    RAG ArticleSource
            ↓
        MCP Client
            ↓
          STDIO
            ↓
    AutoSearch MCP Server
            ↓
       ArticleTool
            ↓
       SearchService
            ↓
    ArticleRepository
            ↓
       MySQL articles

本階段原則：

    1. RAG 不直接操作 SQL。
    2. RAG 不直接操作 Database。
    3. RAG 不直接操作 ArticleRepository。
    4. RAG 透過 MCP 取得 Article。
    5. 使用 Document ID 或 URL 作為 Article identifier。
    6. 不建立 LangChain Document。
    7. 不執行 Embedding。
    8. 不使用 ChromaDB。
    9. 不執行 Chunking。
    10. 不執行 LLM Analysis。
"""


import asyncio
import sys
from pathlib import Path

from mcp import ClientSession
from mcp.client.stdio import (
    stdio_client,
    StdioServerParameters,
)


class ArticleSource:
    """
    RAG-1.1 Article Source。

    負責透過 MCP Client
    從 AutoSearch MCP Server
    取得 Article。

    支援：

        get_by_document_id()
        get_by_url()
    """

    # ==================================================
    # Initialize
    # ==================================================

    def __init__(
        self,
        server_script=None
    ):
        """
        初始化 Article Source。

        Parameters:
            server_script:
                MCP Server 啟動檔案。

                Default:
                    autosearch_mcp/server.py
        """

        if server_script is None:

            project_root = (
                Path(__file__)
                .resolve()
                .parent.parent
            )

            server_script = (
                project_root
                / "autosearch_mcp"
                / "server.py"
            )

        self.server_script = Path(
            server_script
        ).resolve()

        if not self.server_script.exists():

            raise FileNotFoundError(
                "MCP server script not found: "
                f"{self.server_script}"
            )

    # ==================================================
    # MCP Server Parameters
    # ==================================================

    def _create_server_parameters(self):
        """
        建立 MCP STDIO Server Parameters。
        """

        return StdioServerParameters(
            command=sys.executable,
            args=[
                str(
                    self.server_script
                )
            ],
        )

    # ==================================================
    # Call MCP Tool
    # ==================================================

    async def _call_tool(
        self,
        tool_name,
        arguments
    ):
        """
        透過 MCP Client 呼叫 MCP Tool。
        """

        server_parameters = (
            self._create_server_parameters()
        )

        async with stdio_client(
            server_parameters
        ) as (
            read_stream,
            write_stream
        ):

            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments=arguments
                )

                return result

    # ==================================================
    # Parse MCP Result
    # ==================================================

    def _extract_article(
        self,
        result
    ):
        """
        從 MCP Tool Result
        取得 Article data。

        MCP Server 回傳格式：

            {
                "document_id": "...",
                "data": {
                    ...
                }
            }

        或：

            {
                "url": "...",
                "data": {
                    ...
                }
            }
        """

        if result is None:

            return None

        structured_content = getattr(
            result,
            "structuredContent",
            None
        )

        if structured_content is None:

            structured_content = getattr(
                result,
                "structured_content",
                None
            )

        if isinstance(
            structured_content,
            dict
        ):

            data = structured_content.get(
                "data"
            )

            if isinstance(
                data,
                dict
            ):

                return data

        content = getattr(
            result,
            "content",
            None
        )

        if not content:

            return None

        for item in content:

            text = getattr(
                item,
                "text",
                None
            )

            if not text:

                continue

            try:

                import json

                payload = json.loads(
                    text
                )

            except (
                TypeError,
                ValueError
            ):

                continue

            if not isinstance(
                payload,
                dict
            ):

                continue

            data = payload.get(
                "data"
            )

            if isinstance(
                data,
                dict
            ):

                return data

        return None

    # ==================================================
    # Get By Document ID
    # ==================================================

    async def _get_by_document_id(
        self,
        document_id
    ):
        """
        透過 MCP Document ID
        取得 Article。
        """

        if document_id is None:

            return None

        document_id = str(
            document_id
        ).strip()

        if not document_id:

            return None

        result = await self._call_tool(
            "get_article_by_document_id",
            {
                "document_id": document_id
            }
        )

        return self._extract_article(
            result
        )

    # ==================================================
    # Get By URL
    # ==================================================

    async def _get_by_url(
        self,
        url
    ):
        """
        透過 MCP Article URL
        取得 Article。
        """

        if url is None:

            return None

        url = str(
            url
        ).strip()

        if not url:

            return None

        result = await self._call_tool(
            "get_article_by_url",
            {
                "url": url
            }
        )

        return self._extract_article(
            result
        )

    # ==================================================
    # Public API
    # ==================================================

    def get_by_document_id(
        self,
        document_id
    ):
        """
        依 Document ID 取得 Article。

        Returns:
            dict | None
        """

        return asyncio.run(
            self._get_by_document_id(
                document_id
            )
        )

    def get_by_url(
        self,
        url
    ):
        """
        依 URL 取得 Article。

        Returns:
            dict | None
        """

        return asyncio.run(
            self._get_by_url(
                url
            )
        )


__all__ = [
    "ArticleSource"
]