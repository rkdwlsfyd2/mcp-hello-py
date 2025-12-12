#!/usr/bin/env python3
"""
MCP Hello Server + 공공데이터 관광코스 날씨조회 Tool (안정통합버전)

- FastMCP 서버
- Cloud Run 8080 포트 HTTP Stream 정상 지원
- 기본 인사 기능 + 복수 인사 기능
- 공공데이터 관광코스 동네예보 Tool(get_tour_weather_forecast)
- Resource / Prompt 완전 정상 작동
"""

import os
import sys
import requests
import urllib.parse

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ======================================================================
# FastMCP 서버 생성
# ======================================================================

mcp = FastMCP(
    name="mcp-hello",
    instructions="한국어 인사 및 관광코스 날씨 조회 기능을 제공하는 MCP 서버입니다.",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

# ======================================================================
# 인사 Tools
# ======================================================================

@mcp.tool()
def say_hello(name: str) -> str:
    """한 사람에게 인사"""
    if not name or name.strip() == "":
        return "안녕하세요!"
    return f"안녕하세요, {name}님!"


@mcp.tool()
def say_hello_multiple(names: list[str]) -> str:
    """여러 사람에게 인사"""
    if not names:
        return "이름이 없습니다."
    return "\n".join([f"• {say_hello(name)}" for name in names])

# ======================================================================
# 공공데이터 관광코스 동네예보 Tool
# ======================================================================

@mcp.tool()
def get_tour_weather_forecast(current_date: str, hour: int, course_id: int):
    """
    관광코스별 동네예보 조회 Tool
    Args:
        current_date (str): YYYYMMDD
        hour (int): 0~23
        course_id (int): 관광 코스 ID
    """

    base_url = "https://apis.data.go.kr/1360000/TourStnInfoService1/getTourStnVilageFcst1"

    # 공공데이터 서비스 키 (반드시 URL 인코딩)
    service_key = "2b724c413f0e2567470128712f58b426b5be1e350d4956e346d9eabf1260a07d"
    encoded_key = urllib.parse.quote(service_key)

    params = {
        "ServiceKey": encoded_key,
        "pageNo": 1,
        "numOfRows": 10,
        "dataType": "JSON",
        "CURRENT_DATE": current_date,
        "HOUR": hour,
        "COURSE_ID": course_id
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        return {
            "error": f"API 호출 실패: HTTP {response.status_code}",
            "details": response.text
        }

    try:
        return response.json()
    except Exception:
        return {"error": "JSON 변환 실패", "raw": response.text}

# ======================================================================
# Resource
# ======================================================================

@mcp.resource("docs://hello/readme")
def get_readme() -> str:
    """문서 리소스"""
    return """# Hello MCP Server Documentation

## 제공 기능
- say_hello
- say_hello_multiple
- get_tour_weather_forecast

## 날씨 Tool 설명
공공데이터포털 관광코스 동네예보 API를 호출하여
기온, 습도, 하늘상태 등의 정보를 반환합니다.
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
- 정중하고 친근하게
- 3~5 문장
"""

# ======================================================================
# Main Entry (Cloud Run은 무조건 HTTP Stream 모드로 실행)
# ======================================================================

def main():
    port = int(os.environ.get("PORT", 8080))
    mcp.settings.port = port
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
