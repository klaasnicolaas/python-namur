"""Test the models."""

from __future__ import annotations

import pytest
from aresponses import ResponsesMockServer
from syrupy.assertion import SnapshotAssertion

from namur import ODPNamur, ODPNamurResultsError, ParkingSpot, ParkingType

from . import load_fixtures


async def test_parking_model(
    aresponses: ResponsesMockServer,
    snapshot: SnapshotAssertion,
    odp_namur_client: ODPNamur,
) -> None:
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
    locations: list[ParkingSpot] = await odp_namur_client.parking_spaces(
        parking_type=ParkingType.NORMAL
    )
    assert locations == snapshot


async def test_no_parking_results(
    aresponses: ResponsesMockServer, odp_namur_client: ODPNamur
) -> None:
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
    with pytest.raises(ODPNamurResultsError):
        await odp_namur_client.parking_spaces(parking_type=ParkingType.PMR)
