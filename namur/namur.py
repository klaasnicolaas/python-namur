"""Asynchronous Python client providing Open Data information of Namur."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any

import aiohttp
import async_timeout
from aiohttp import hdrs
from yarl import URL

from .exceptions import (
    ODPNamurConnectionError,
    ODPNamurError,
    ODPNamurResultsError,
    ODPNamurTypeError,
)
from .models import ParkingSpot


@dataclass
class ODPNamur:
    """Main class for handling data fetchting from Open Data Platform of Namur."""

    request_timeout: float = 10.0
    session: aiohttp.client.ClientSession | None = None

    _close_session: bool = False

    @staticmethod
    async def define_type(parking_type: int) -> str:
        """Define the parking type.

        Args:
            parking_type: The selected parking type number.

        Returns:
            The parking type as string.

        Raises:
            ODPNamurTypeError: If the parking type is not listed.
        """
        options = {
            1: "Place normale",
            2: "Devant accès/garage",
            3: "PMR",
            4: "Dépose-minute",
            5: "Livraison",
            6: "Police",
            7: "Taxi",
            8: "Car-sharing",
            9: "Recyclage",
            10: "Car",
            11: "Bus scolaire",
            12: "Borne électrique",
            13: "Réservé",
        }.get(parking_type)

        # Check if the parking type is listed
        if options is None:
            raise ODPNamurTypeError(
                "The selected number does not match the list of parking types"
            )
        return options

    async def _request(
        self,
        uri: str,
        *,
        method: str = hdrs.METH_GET,
        params: dict[str, Any] | None = None,
    ) -> Any:
        """Handle a request to the Open Data Platform API of Namur.

        Args:
            uri: Request URI, without '/', for example, 'status'
            method: HTTP method to use, for example, 'GET'
            params: Extra options to improve or limit the response.

        Returns:
            A Python dictionary (json) with the response from
            the Open Data Platform API of Namur.

        Raises:
            ODPNamurConnectionError: An error occurred while
                communicating with the Open Data Platform API.
            ODPNamurError: Received an unexpected response from
                the Open Data Platform API.
        """
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https", host="data.namur.be", path="/api/records/1.0/"
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonNamur/{version}",
        }

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                response = await self.session.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    ssl=True,
                )
                response.raise_for_status()
        except asyncio.TimeoutError as exception:
            raise ODPNamurConnectionError(
                "Timeout occurred while connecting to the Open Data Platform API."
            ) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise ODPNamurConnectionError(
                "Error occurred while communicating with the Open Data Platform API."
            ) from exception

        content_type = response.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            text = await response.text()
            raise ODPNamurError(
                "Unexpected content type response from the Open Data Platform API",
                {"Content-Type": content_type, "response": text},
            )

        return await response.json()

    async def parking_spaces(
        self, limit: int = 10, parking_type: int = 1
    ) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
            limit: Number of rows to return.
            parking_type: The selected parking type number.

        Returns:
            A list of ParkingSpot objects.

        Raises:
            ODPNamurResultsError: When no results are found.
        """
        results: list[ParkingSpot] = []
        locations = await self._request(
            "search/",
            params={
                "dataset": "namur-parking-emplacements",
                "rows": limit,
                "refine.type_parking": await self.define_type(parking_type),
            },
        )

        for item in locations["records"]:
            results.append(ParkingSpot.from_json(item))
        if not results:
            raise ODPNamurResultsError("No parking locations were found")
        return results

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> ODPNamur:
        """Async enter.

        Returns:
            The Open Data Platform Namur object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
            _exc_info: Exec type.
        """
        await self.close()
