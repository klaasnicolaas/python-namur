"""Asynchronous Python client providing Open Data information of Namur."""
from __future__ import annotations

import asyncio
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Self, cast

from aiohttp import ClientError, ClientSession
from aiohttp.hdrs import METH_GET
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
    session: ClientSession | None = None

    _close_session: bool = False

    @staticmethod
    async def define_type(parking_type: int) -> str:
        """Define the parking type.

        Args:
        ----
            parking_type: The selected parking type number.

        Returns:
        -------
            The parking type as string.

        Raises:
        ------
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
            msg = "The selected number does not match the list of parking types"
            raise ODPNamurTypeError(
                msg,
            )
        return options

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
        version = metadata.version(__package__)
        url = URL.build(
            scheme="https",
            host="data.namur.be",
            path="/api/records/1.0/",
        ).join(URL(uri))

        headers = {
            "Accept": "application/json, text/plain",
            "User-Agent": f"PythonNamur/{version}",
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
        except asyncio.TimeoutError as exception:
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

        return cast(dict[str, Any], await response.json())

    async def parking_spaces(
        self,
        limit: int = 10,
        parking_type: int = 1,
    ) -> list[ParkingSpot]:
        """Get all the parking locations.

        Args:
        ----
            limit: Number of rows to return.
            parking_type: The selected parking type number.

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
                "refine.type_parking": await self.define_type(parking_type),
            },
        )

        results: list[ParkingSpot] = [
            ParkingSpot.from_json(item) for item in locations["records"]
        ]
        if not results:
            msg = "No parking locations were found"
            raise ODPNamurResultsError(msg)
        return results

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
