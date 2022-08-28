# pylint: disable=W0621
"""Asynchronous Python client providing Open Data information of Namur."""

import asyncio

from namur import ODPNamur


async def main() -> None:
    """Show example on using the Namur API client."""
    async with ODPNamur() as client:
        parking_spaces = await client.parking_spaces(limit=10, parking_type=3)

        count: int
        for index, item in enumerate(parking_spaces, 1):
            count = index
            print(item)

        print("__________________________")
        print(f"Total locations found: {count}")


if __name__ == "__main__":
    asyncio.run(main())
