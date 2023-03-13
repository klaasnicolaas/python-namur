"""Basic tests for the Open Data Platform API of Namur."""
# pylint: disable=protected-access
import asyncio
from unittest.mock import patch

import pytest
from aiohttp import ClientError, ClientResponse, ClientSession
from aresponses import Response, ResponsesMockServer

from namur import ODPNamur
from namur.exceptions import ODPNamurConnectionError, ODPNamurError

from . import load_fixtures


async def test_json_request(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "data.namur.be",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking_pmr.json"),
        ),
    )
    async with ClientSession() as session:
        client = ODPNamur(session=session)
        response = await client._request("test")
        assert response is not None
        await client.close()


async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test internal session is handled correctly."""
    aresponses.add(
        "data.namur.be",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking_pmr.json"),
        ),
    )
    async with ODPNamur() as client:
        await client._request("test")


async def test_timeout(aresponses: ResponsesMockServer) -> None:
    """Test request timeout is handled correctly."""
    # Faking a timeout by sleeping
    async def reponse_handler(_: ClientResponse) -> Response:
        await asyncio.sleep(0.2)
        return aresponses.Response(
            body="Goodmorning!",
            text=load_fixtures("parking_pmr.json"),
        )

    aresponses.add("data.namur.be", "/api/records/1.0/test", "GET", reponse_handler)

    async with ClientSession() as session:
        client = ODPNamur(session=session, request_timeout=0.1)
        with pytest.raises(ODPNamurConnectionError):
            assert await client._request("test")


async def test_content_type(aresponses: ResponsesMockServer) -> None:
    """Test request content type error is handled correctly."""
    aresponses.add(
        "data.namur.be",
        "/api/records/1.0/test",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "blabla/blabla"},
        ),
    )

    async with ClientSession() as session:
        client = ODPNamur(
            session=session,
        )
        with pytest.raises(ODPNamurError):
            assert await client._request("test")


async def test_client_error() -> None:
    """Test request client error is handled correctly."""
    async with ClientSession() as session:
        client = ODPNamur(session=session)
        with patch.object(
            session,
            "request",
            side_effect=ClientError,
        ), pytest.raises(ODPNamurConnectionError):
            assert await client._request("test")
