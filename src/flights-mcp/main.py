import os
import httpx
from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

API_TOKEN = os.environ.get("FLIGHTS_AVIASALES_API_TOKEN", "")
MARKER = os.environ.get("FLIGHTS_AVIASALES_MARKER", "")
BASE_URL = "https://api.travelpayouts.com"
HEADERS = {"X-Access-Token": API_TOKEN}

mcp = FastMCP(
    "Travelpayouts Data",
    transport=os.environ.get("FLIGHTS_TRANSPORT", "sse"),
    host="0.0.0.0",
    port=int(os.environ.get("FLIGHTS_HTTP_PORT", 4200)),
    path=os.environ.get("FLIGHTS_HTTP_PATH", "/mcp"),
)


@mcp.tool()
async def search_cheap_flights(
    origin: str,
    destination: str,
    depart_date: str = "",
    return_date: str = "",
    currency: str = "rub",
) -> dict:
    """
    Search cheapest flights (non-stop + 1-2 stops) between two cities.
    origin/destination: IATA code, e.g. MOW, ALA, LED.
    depart_date / return_date: optional, format YYYY-MM or YYYY-MM-DD.
    currency: rub (default), usd, eur, etc.
    """
    params = {
        "origin": origin,
        "destination": destination,
        "currency": currency,
        "token": API_TOKEN,
    }
    if depart_date:
        params["depart_date"] = depart_date
    if return_date:
        params["return_date"] = return_date

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v1/prices/cheap", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


@mcp.tool()
async def search_direct_flights(
    origin: str,
    destination: str,
    depart_date: str = "",
    return_date: str = "",
    currency: str = "rub",
) -> dict:
    """
    Search cheapest NON-STOP flights only between two cities.
    depart_date / return_date: optional, format YYYY-MM or YYYY-MM-DD.
    """
    params = {
        "origin": origin,
        "destination": destination,
        "currency": currency,
        "token": API_TOKEN,
    }
    if depart_date:
        params["depart_date"] = depart_date
    if return_date:
        params["return_date"] = return_date

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v1/prices/direct", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


@mcp.tool()
async def price_calendar(
    origin: str,
    destination: str,
    depart_date: str,
    return_date: str = "",
    currency: str = "rub",
) -> dict:
    """
    Get cheapest prices for each day of a selected month.
    depart_date: format YYYY-MM (e.g. 2026-07).
    """
    params = {
        "origin": origin,
        "destination": destination,
        "depart_date": depart_date,
        "calendar_type": "departure_date",
        "currency": currency,
        "token": API_TOKEN,
    }
    if return_date:
        params["return_date"] = return_date

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v1/prices/calendar", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


@mcp.tool()
async def latest_prices(
    origin: str = "",
    destination: str = "",
    currency: str = "rub",
    one_way: bool = False,
    limit: int = 30,
    sorting: str = "price",
) -> dict:
    """
    Get latest prices found in last 48 hours.
    sorting: price | route | distance_unit_price.
    """
    params = {
        "currency": currency,
        "period_type": "year",
        "page": 1,
        "limit": limit,
        "show_to_affiliates": "true",
        "sorting": sorting,
        "one_way": str(one_way).lower(),
        "token": API_TOKEN,
    }
    if origin:
        params["origin"] = origin
    if destination:
        params["destination"] = destination

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v2/prices/latest", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


@mcp.tool()
async def month_price_matrix(
    origin: str,
    destination: str,
    month: str = "",
    currency: str = "rub",
) -> dict:
    """
    Prices for each day of a month grouped by stops.
    month: format YYYY-MM-DD (first day), e.g. 2026-07-01.
    """
    params = {
        "origin": origin,
        "destination": destination,
        "show_to_affiliates": "true",
        "currency": currency,
        "token": API_TOKEN,
    }
    if month:
        params["month"] = month

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v2/prices/month-matrix", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


@mcp.tool()
async def popular_destinations(
    origin: str,
    currency: str = "rub",
) -> dict:
    """
    Get most popular flight destinations from a city.
    origin: IATA code, e.g. MOW.
    """
    params = {"origin": origin, "currency": currency, "token": API_TOKEN}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v1/city-directions", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


@mcp.tool()
async def airline_popular_routes(
    airline_code: str,
    limit: int = 20,
) -> dict:
    """
    Most popular routes for an airline.
    airline_code: IATA code, e.g. SU (Aeroflot), S7.
    """
    params = {"airline_code": airline_code, "limit": limit, "token": API_TOKEN}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(f"{BASE_URL}/v1/airline-directions", headers=HEADERS, params=params)
    if not resp.is_success:
        raise ToolError(f"API error {resp.status_code}: {resp.text}")
    data = resp.json()
    if not data.get("success"):
        raise ToolError(f"API returned error: {data.get('error')}")
    return data


if __name__ == "__main__":
    mcp.run()
