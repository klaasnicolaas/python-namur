"""Complete parking collection and failure boundaries."""

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


async def test_complete_collection(odp_namur_client: ODPNamur) -> None:
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
        collection = await odp_namur_client.parking_collection(ParkingType.PMR)
    assert collection.complete
    assert collection.total_count == len(collection.records) == 201
    assert collection.pages_fetched == 3
    assert collection.source_version == "version"
    assert collection.records[0].source_attributes == data[0]["fields"]
    assert collection.records[0].source_attributes["horaire"]
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
async def test_invalid_collection(page: dict, odp_namur_client: ODPNamur) -> None:
    """Unsupported counts, short pages and invalid identities fail closed."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(ODPNamur, "_request", AsyncMock(return_value=page)),
        pytest.raises(ODPNamurResultsError),
    ):
        await odp_namur_client.parking_collection(ParkingType.PMR)


async def test_changed_count(odp_namur_client: ODPNamur) -> None:
    """Count changes between pages cannot produce complete collections."""
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
        await odp_namur_client.parking_collection(ParkingType.PMR)


async def test_changed_version(odp_namur_client: ODPNamur) -> None:
    """Processing changes invalidate even an otherwise complete result."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(side_effect=["a", "b"])),
        patch.object(
            ODPNamur, "_request", AsyncMock(return_value={"nhits": 0, "records": []})
        ),
        pytest.raises(ODPNamurResultsError, match="Dataset changed"),
    ):
        await odp_namur_client.parking_collection(ParkingType.PMR)


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


async def test_empty_collection(odp_namur_client: ODPNamur) -> None:
    """An empty selection is a complete successful collection."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(
            ODPNamur, "_request", AsyncMock(return_value={"nhits": 0, "records": []})
        ),
    ):
        collection = await odp_namur_client.parking_collection(ParkingType.PMR)
    assert collection.records == []
    assert collection.total_count == 0
    assert collection.pages_fetched == 1
    assert collection.source_version == "version"
    assert collection.complete


@pytest.mark.parametrize("max_records", [0, -1, True, False, 1.5, "10", None, 10001])
async def test_invalid_max_records(
    max_records: object, odp_namur_client: ODPNamur
) -> None:
    """Reject invalid limits before requesting the source."""
    with (
        patch.object(ODPNamur, "_request", AsyncMock()) as request,
        pytest.raises(ValueError, match="max_records"),
    ):
        await odp_namur_client.parking_collection(max_records=max_records)  # ty: ignore[invalid-argument-type]
    request.assert_not_awaited()


async def test_max_records_never_truncates(odp_namur_client: ODPNamur) -> None:
    """A configured safety ceiling rejects the whole oversized selection."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(
            ODPNamur,
            "_request",
            AsyncMock(return_value={"nhits": 2, "records": records(2)}),
        ),
        pytest.raises(ODPNamurResultsError, match="unsupported"),
    ):
        await odp_namur_client.parking_collection(ParkingType.PMR, max_records=1)


async def test_max_records_boundary(odp_namur_client: ODPNamur) -> None:
    """A selection exactly at the configured ceiling succeeds in full."""
    with (
        patch.object(ODPNamur, "dataset_version", AsyncMock(return_value="version")),
        patch.object(
            ODPNamur,
            "_request",
            AsyncMock(return_value={"nhits": 1, "records": records(1)}),
        ),
    ):
        collection = await odp_namur_client.parking_collection(
            ParkingType.PMR, max_records=1
        )
    assert len(collection.records) == collection.total_count == 1
    assert collection.complete
