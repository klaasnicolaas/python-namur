"""Complete snapshot collection and failure boundaries."""

import json
from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest
from aresponses import ResponsesMockServer

from namur import ODPNamur, ODPNamurResultsError, ParkingType

from . import load_fixtures


def records(count: int) -> list[dict]:
    """Build realistic records with distinct source identifiers."""
    record = json.loads(load_fixtures("parking_pmr.json"))["records"][0]
    result = []
    for number in range(count):
        item = deepcopy(record)
        item["fields"]["identifiant"] = str(number)
        result.append(item)
    return result


async def test_complete_snapshot(odp_namur_client: ODPNamur) -> None:
    """All pages, source restrictions and version metadata are retained."""
    data = records(201)
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(
            ODPNamur,
            "_request",
            AsyncMock(
                side_effect=[
                    {"nhits": 201, "records": data[:100]},
                    {"nhits": 201, "records": data[100:200]},
                    {"nhits": 201, "records": data[200:]},
                ]
            ),
        ) as request,
    ):
        snapshot = await odp_namur_client.parking_snapshot(ParkingType.PMR)
    assert snapshot.complete
    assert snapshot.total_count == len(snapshot.records) == 201
    assert snapshot.pages_fetched == 3
    assert snapshot.data_processed == "version"
    assert snapshot.records[0].source_attributes == data[0]["fields"]
    assert snapshot.records[0].source_attributes["horaire"]
    assert [call.kwargs["params"]["start"] for call in request.call_args_list] == [
        0,
        100,
        200,
    ]
    assert request.call_args.kwargs["params"]["sort"] == "identifiant"
    assert request.call_args.kwargs["params"]["refine.type_parking"] == "PMR"


@pytest.mark.parametrize(
    "page",
    [
        {"nhits": 10001, "records": []},
        {"nhits": True, "records": []},
        {"nhits": -1, "records": []},
        {"records": []},
        {"nhits": 1, "records": []},
        {"nhits": 0, "records": records(1)},
        {"nhits": 2, "records": records(1) * 2},
        {"nhits": 1, "records": [{"fields": {"identifiant": " "}}]},
        {"nhits": 1, "records": [{"fields": {"identifiant": "x"}}]},
    ],
)
async def test_invalid_snapshot(page: dict, odp_namur_client: ODPNamur) -> None:
    """Unsupported counts, short pages and invalid identities fail closed."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(ODPNamur, "_request", AsyncMock(return_value=page)),
        pytest.raises(ODPNamurResultsError),
    ):
        await odp_namur_client.parking_snapshot(ParkingType.PMR)


async def test_changed_count(odp_namur_client: ODPNamur) -> None:
    """Count changes between pages cannot produce complete snapshots."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(
            ODPNamur,
            "_request",
            AsyncMock(
                side_effect=[
                    {"nhits": 101, "records": records(100)},
                    {"nhits": 102, "records": records(2)},
                ]
            ),
        ),
        pytest.raises(ODPNamurResultsError, match="count changed"),
    ):
        await odp_namur_client.parking_snapshot(ParkingType.PMR)


async def test_changed_version(odp_namur_client: ODPNamur) -> None:
    """Processing changes invalidate even an otherwise complete result."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(side_effect=["a", "b"])),
        patch.object(
            ODPNamur, "_request", AsyncMock(return_value={"nhits": 0, "records": []})
        ),
        pytest.raises(ODPNamurResultsError, match="Dataset changed"),
    ):
        await odp_namur_client.parking_snapshot(ParkingType.PMR)


@pytest.mark.parametrize(
    "metadata",
    [
        {},
        {"metas": {"default": {"data_processed": ""}}},
        {"metas": {"default": {"data_processed": None}}},
    ],
)
async def test_missing_version(metadata: dict, odp_namur_client: ODPNamur) -> None:
    """Missing versions cannot assert source stability."""
    with (
        patch.object(ODPNamur, "_request", AsyncMock(return_value=metadata)),
        pytest.raises(ODPNamurResultsError, match="processing timestamp"),
    ):
        await odp_namur_client.dataset_version()


async def test_metadata_endpoint(
    aresponses: ResponsesMockServer, odp_namur_client: ODPNamur
) -> None:
    """Dataset metadata uses the absolute Explore API path."""
    aresponses.add(
        "data.namur.be",
        "/api/explore/v2.1/catalog/datasets/namur-parking-emplacements",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text=json.dumps({"metas": {"default": {"data_processed": "version"}}}),
        ),
    )
    assert await odp_namur_client.dataset_version() == "version"
