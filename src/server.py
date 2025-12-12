#!/usr/bin/env python3
"""
Simple Hello MCP Server

이 모듈은 이름을 받아 한국어로 인사하는 간단한 MCP 서버를 제공합니다.
"""

import os
import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ======================================================================
# FastMCP 서버 생성
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
# Tools (도구)
# ======================================================================

@mcp.tool()
def say_hello(name: str) -> str:
    """
    이름을 받아 한국어로 인사합니다.
    """
    if not name or name.strip() == "":
        return "안녕하세요!"
    return f"안녕하세요, {name}님!"


@mcp.tool()
def say_hello_multiple(names: list[str]) -> str:
    """
    여러 사람에게 한 번에 인사합니다.
    """
    if not names:
        return ""
    greetings = [f"• 안녕하세요, {name}님!" for name in names]
    return "\n".join(greetings)

# ======================================================================
# Resources (리소스)
# ======================================================================

@mcp.resource("docs://hello/readme")
def get_readme() -> str:
    return """# Hello MCP Server Documentation

## 개요
이름을 받아 한국어로 인사하는 간단한 MCP 서버입니다.

## 사용 가능한 도구
### say_hello
### say_hello_multiple
"""

# ======================================================================
# Prompts (프롬프트)
# ======================================================================

@mcp.prompt()
def greeting_message(recipient: str) -> str:
    greeting = say_hello(recipient)
    return f"""{recipient}님에게 보낼 인사 메시지를 작성하세요.

시작 문장:
{greeting}
"""

# ======================================================================
# Main Entry Point — Cloud Run HTTP Stream 모드
# ======================================================================

def main():
    port = int(os.environ.get("PORT", 8080))
    mcp.settings.port = port
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
