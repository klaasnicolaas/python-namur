"""Test the models."""
import aiohttp
import pytest
from aresponses import ResponsesMockServer

from namur import ODPNamur, ODPNamurResultsError, ODPNamurTypeError, ParkingSpot

from . import load_fixtures


@pytest.mark.asyncio
async def test_parking_model(aresponses: ResponsesMockServer) -> None:
    """Test the parking model."""
    aresponses.add(
        "data.namur.be",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking_pmr.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ODPNamur(session=session)
        locations: list[ParkingSpot] = await client.parking_spaces(parking_type=1)
        for item in locations:
            assert item.spot_id is not None
            assert item.street is not None
            assert item.updated_at is not None


@pytest.mark.asyncio
async def test_no_parking_results(aresponses: ResponsesMockServer) -> None:
    """Test if there are no parking results."""
    aresponses.add(
        "data.namur.be",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("no_parking.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ODPNamur(session=session)
        with pytest.raises(ODPNamurResultsError):
            locations: list[ParkingSpot] = await client.parking_spaces(parking_type=3)
            assert locations == []


@pytest.mark.asyncio
async def test_no_parking_type(aresponses: ResponsesMockServer) -> None:
    """Test when parking_type doesn't exist."""
    aresponses.add(
        "data.namur.be",
        "/api/records/1.0/search/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=load_fixtures("parking_pmr.json"),
        ),
    )
    async with aiohttp.ClientSession() as session:
        client = ODPNamur(session=session)
        with pytest.raises(ODPNamurTypeError):
            locations: list[ParkingSpot] = await client.parking_spaces(parking_type=20)
            assert locations == []
