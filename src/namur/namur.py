"""Asynchronous Python client providing Open Data information of Namur."""

from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
from yarl import URL

from .exceptions import (
    ODPNamurConnectionError,
    ODPNamurError,
    ODPNamurResultsError,
)
from .models import ParkingCollection, ParkingSpot, ParkingType

VERSION = metadata.version("namur")


@dataclass
class ODPNamur:
    """Main class for handling data fetchting from Open Data Platform of Namur."""

    request_timeout: float = 10.0
    session: ClientSession | None = None

    _close_session: bool = False

    async def _request(
        self,
        uri: str,
        *,
        method: str = METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Namur.

        Args:
        ----
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
        -------
            A Python dictionary (json) with the response from
            the Open Data Platform API of Namur.

        Raises:
        ------
            ODPNamurConnectionError: An error occurred while
                communicating with the Open Data Platform API.
            ODPNamurError: Received an unexpected response from
                the Open Data Platform API.

        """
        url = URL.build(
            scheme="https",
            host="data.namur.be",
            path="/api/records/1.0/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonNamur/{VERSION}",
        }

        if self.session is None:
            self.session = ClientSession()
            self._close_session = True

        try:
            async with asyncio.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except TimeoutError as exception:
            msg = "Timeout occurred while connecting to the Open Data Platform API."
            raise ODPNamurConnectionError(
                msg,
            ) from exception
        except (ClientError, socket.gaierror) as exception:
            msg = "Error occurred while communicating with the Open Data Platform API."
            raise ODPNamurConnectionError(
                msg,
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            msg = "Unexpected content type response from the Open Data Platform API"
            raise ODPNamurError(
                msg,
                {"Content-Type": content_type, "response": text},
            )

        return await response.json()

    async def parking_spaces(
        self,
        limit: int = 10,
        parking_type: ParkingType = ParkingType.NORMAL,
    ) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
        ----
            limit: Number of rows to return.
            parking_type (enum): The selected parking type.

        Returns:
        -------
            A list of ParkingSpot objects.

        Raises:
        ------
            ODPNamurResultsError: When no results are found.

        """
        locations = await self._request(
            "search/",
            params={
                "dataset": "namur-parking-emplacements",
                "rows": limit,
                "refine.type_parking": parking_type.value,
            },
        )

        results: list[ParkingSpot] = [
            ParkingSpot.from_json(item) for item in locations["records"]
        ]
        if not results:
            msg = "No parking locations were found"
            raise ODPNamurResultsError(msg)
        return results

    async def dataset_version(self) -> str:
        """Return the dataset processing timestamp used to detect source changes."""
        metadata_response = await self._request(
            "/api/explore/v2.1/catalog/datasets/namur-parking-emplacements"
        )
        try:
            version = metadata_response["metas"]["default"]["data_processed"]
        except (KeyError, TypeError) as exception:
            msg = "Missing dataset processing timestamp"
            raise ODPNamurResultsError(msg) from exception
        if not isinstance(version, str) or not version.strip():
            msg = "Missing dataset processing timestamp"
            raise ODPNamurResultsError(msg)
        return version

    async def parking_collection(
        self,
        parking_type: ParkingType = ParkingType.NORMAL,
        *,
        max_records: int = 10000,
    ) -> ParkingCollection:
        """Fetch every selected record, rejecting observed collection inconsistencies.

        Opendatasoft record searches allow offsets up to 10,000 records. Larger
        selections or those above max_records raise instead of being truncated.
        Processing revision checks do not provide a transactional source snapshot.
        The existing parking_spaces method remains available for capped requests.
        """
        if type(max_records) is not int or not 0 < max_records <= 10000:
            msg = "max_records must be an integer between 1 and 10000"
            raise ValueError(msg)
        version = await self.dataset_version()
        results: list[ParkingSpot] = []
        identifiers: set[str] = set()
        total_count: int | None = None
        pages_fetched = 0
        while total_count is None or len(results) < total_count:
            page = await self._request(
                "search/",
                params={
                    "dataset": "namur-parking-emplacements",
                    "rows": 100,
                    "start": len(results),
                    "sort": "identifiant",
                    "refine.type_parking": parking_type.value,
                },
            )
            count = page.get("nhits")
            records = page.get("records")
            if (
                type(count) is not int
                or count < 0
                or count > max_records
                or not isinstance(records, list)
            ):
                msg = "Invalid or unsupported parking collection response"
                raise ODPNamurResultsError(msg)
            if total_count is None:
                total_count = count
            if count != total_count:
                msg = "Parking count changed during collection"
                raise ODPNamurResultsError(msg)
            if len(records) != min(100, total_count - len(results)):
                msg = "Incomplete parking collection page"
                raise ODPNamurResultsError(msg)
            for record in records:
                try:
                    identifier = record["fields"]["identifiant"]
                    spot = ParkingSpot.from_json(record)
                except (KeyError, TypeError, ValueError, IndexError) as exception:
                    msg = "Invalid or duplicate parking record in collection"
                    raise ODPNamurResultsError(msg) from exception
                if (
                    not isinstance(identifier, str)
                    or not identifier.strip()
                    or identifier in identifiers
                ):
                    msg = "Invalid or duplicate parking identifier in collection"
                    raise ODPNamurResultsError(msg)
                identifiers.add(identifier)
                results.append(spot)
            pages_fetched += 1
        if await self.dataset_version() != version:
            msg = "Dataset changed during parking collection"
            raise ODPNamurResultsError(msg)
        return ParkingCollection(
            records=results,
            total_count=total_count,
            pages_fetched=pages_fetched,
            source_version=version,
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> Self:
        """Async enter.

        Returns
        -------
            The Open Data Platform Namur object.

        """
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        """Async exit.

        Args:
        ----
            _exc_info: Exec type.

        """
        await self.close()
