"""Fixture for the ODP Namur tests."""

from collections.abc import AsyncGenerator

import pytest
from aiohttp import ClientSession

from namur import ODPNamur


@pytest.fixture(name="odp_namur_client")
async def client() -> AsyncGenerator[ODPNamur, None]:
    """Return an ODP Namur client."""
    async with (
        ClientSession() as session,
        ODPNamur(session=session) as odp_namur_client,
    ):
        yield odp_namur_client
