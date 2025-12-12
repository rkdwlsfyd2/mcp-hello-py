#!/usr/bin/env python3
import os
import sys

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ======================================================================
# MCP 서버 생성
# ======================================================================

mcp = FastMCP(
    name="mcp-hello",
    instructions="이름을 받아 한국어로 인사하는 간단한 MCP 서버입니다.",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

# ======================================================================
# Tools
# ======================================================================

@mcp.tool()
def say_hello(name: str) -> str:
    """한 사람에게 한국어로 인사합니다."""
    if not name or name.strip() == "":
        return "안녕하세요!"
    return f"안녕하세요, {name}님!"


@mcp.tool()
def say_hello_multiple(names: list[str]) -> str:
    """여러 사람에게 인사"""
    if not names:
        return "이름이 없습니다."
    return "\n".join([f"• 안녕하세요, {name}님!" for name in names])

# ======================================================================
# Resource
# ======================================================================

@mcp.resource("docs://hello/readme")
def get_readme() -> str:
    return """# Hello MCP Server Documentation

이 서버는 인사 기능을 제공합니다.
"""

# ======================================================================
# Prompt
# ======================================================================

@mcp.prompt()
def greeting_message(recipient: str) -> str:
    greeting = say_hello(recipient)
    return f"""{recipient}님에게 보낼 인사 메시지를 작성하세요.

시작 문장:
{greeting}

조건:
- 친근함
- 3~5 문장
"""

# ======================================================================
# Main 실행 (Cloud Run에서는 무조건 HTTP Stream 모드)
# ======================================================================

def main():
    port = int(os.environ.get("PORT", 8080))
    mcp.settings.port = port
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
