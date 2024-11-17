# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Namur."""

import asyncio

from namur import ODPNamur, ParkingType


async def main() -> None:
    """Show example on using the Namur API client."""
    async with ODPNamur() as client:
        parking_spaces = await client.parking_spaces(
            limit=10, parking_type=ParkingType.PMR
        )

        count: int = len(parking_spaces)
        for item in parking_spaces:
            print(item)

        print("__________________________")
        print(f"Total locations found: {count}")


if __name__ == "__main__":
    asyncio.run(main())
