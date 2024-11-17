"""Asynchronous Python client providing Open Data information of Namur."""

from .exceptions import (
    ODPNamurConnectionError,
    ODPNamurError,
    ODPNamurResultsError,
)
from .models import ParkingSpot, ParkingType
from .namur import ODPNamur

__all__ = [
    "ODPNamur",
    "ODPNamurConnectionError",
    "ODPNamurError",
    "ODPNamurResultsError",
    "ParkingSpot",
    "ParkingType",
]
