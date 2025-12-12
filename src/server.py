#!/usr/bin/env python3
import os
import requests          # 🔹 위로 올리기
import urllib.parse      # 🔹 위로 올리기

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

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

# ---------- 기존 인사 도구 ----------
@mcp.tool()
def say_hello(name: str) -> str:
    ...

@mcp.tool()
def say_hello_multiple(names: list[str]) -> str:
    ...

# ---------- 🔹 새로 추가한 날씨 도구 ----------
@mcp.tool()
def get_tour_weather_forecast(current_date: str, hour: int, course_id: int):
    """
    관광코스별 동네예보를 조회합니다.
    """
    base_url = "https://apis.data.go.kr/1360000/TourStnInfoService1/getTourStnVilageFcst1"

    service_key = "2b724c413f0e2567470128712f58b426b5be1e350d4956e346d9eabf1260a07d"
    encoded_key = urllib.parse.quote(service_key)

    params = {
        "ServiceKey": encoded_key,
        "pageNo": 1,
        "numOfRows": 10,
        "dataType": "JSON",
        "CURRENT_DATE": current_date,
        "HOUR": hour,
        "COURSE_ID": course_id,
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        return {"error": f"API 호출 실패: {response.status_code}", "details": response.text}

    try:
        return response.json()
    except Exception:
        return {"error": "JSON 변환 실패", "raw": response.text}

# ---------- Resource / Prompt 그대로 유지 ----------
@mcp.resource("docs://hello/readme")
def get_readme() -> str:
    ...

@mcp.prompt()
def greeting_message(recipient: str) -> str:
    ...

# ---------- 메인 진입점 (맨 마지막에만 남기기) ----------
def main():
    import sys
    if "--http-stream" in sys.argv:
        port = int(os.environ.get("PORT", 8080))
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")

if __name__ == "__main__":
    main()
