#!/usr/bin/env python3
"""
MCP Hello + 공공데이터 관광코스 동네예보 Tool 포함 서버

- FastMCP 기반
- Cloud Run HTTP Stream 지원
- 인사 도구, 복수 인사 도구
- 날씨 조회 Tool(get_tour_weather_forecast)
- Resource / Prompt 지원
"""

import os
import sys
import requests
import urllib.parse

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# ======================================================================
# MCP 서버 생성
# ======================================================================

mcp = FastMCP(
    name="mcp-hello",
    instructions="이름을 받아 인사하거나 관광지 동네예보를 조회하는 MCP 서버입니다.",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False,
    ),
)

# ======================================================================
# 인사 관련 도구
# ======================================================================

@mcp.tool()
def say_hello(name: str) -> str:
    if not name or name.strip() == "":
        return "안녕하세요!"
    return f"안녕하세요, {name}님!"


@mcp.tool()
def say_hello_multiple(names: list[str]) -> str:
    if not names:
        return "이름이 없습니다."

    greetings = [f"• {say_hello(name)}" for name in names]
    return "\n".join(greetings)

# ======================================================================
# 관광코스 동네예보 조회 도구
# ======================================================================

@mcp.tool()
def get_tour_weather_forecast(current_date: str, hour: int, course_id: int):
    """
    관광코스별 동네예보 조회 Tool

    Args:
        current_date (str): YYYYMMDD
        hour (int): 0~23
        course_id (int): 지역 관광 코스 ID
    """

    base_url = "https://apis.data.go.kr/1360000/TourStnInfoService1/getTourStnVilageFcst1"

    # 너의 인증키 (반드시 URL Encoding)
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
            "error": f"API 호출 실패 (HTTP {response.status_code})",
            "details": response.text
        }

    # JSON 파싱
    try:
        return response.json()
    except Exception:
        return {
            "error": "JSON 파싱 실패",
            "raw": response.text
        }

# ======================================================================
# 문서(Resource)
# ======================================================================

@mcp.resource("docs://hello/readme")
def get_readme() -> str:
    return """# Hello MCP Server 사용 가이드

이 서버는 아래 기능을 제공합니다:

## 1) say_hello
한 사람에게 인사합니다.

## 2) say_hello_multiple
여러 사람에게 한 번에 인사합니다.

## 3) get_tour_weather_forecast
공공데이터포털 관광코스별 동네예보 API를 호출합니다.
"""

# ======================================================================
# 프롬프트
# ======================================================================

@mcp.prompt()
def greeting_message(recipient: str) -> str:
    greeting = say_hello(recipient)
    return f"""{recipient}님에게 보낼 인사 메시지를 작성하세요.

다음 형식으로 시작하세요:
{greeting}

톤: 친근하고 공손하게
길이: 3~5 문장
"""

# ======================================================================
# 메인 엔트리포인트 (절대 아래에 Tool을 두지 말 것!!)
# ======================================================================

def main():
    """Cloud Run 또는 STDIO 모드 선택 실행"""
    if "--http-stream" in sys.argv:
        port = int(os.getenv("PORT", "8080"))
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
