"""Asynchronous Python client providing Open Data information of Namur."""

from .exceptions import (
    ODPNamurConnectionError,
    ODPNamurError,
    ODPNamurResultsError,
    ODPNamurTypeError,
)
from .models import ParkingSpot
from .namur import ODPNamur

__all__ = [
    "ODPNamur",
    "ODPNamurConnectionError",
    "ODPNamurError",
    "ODPNamurResultsError",
    "ODPNamurTypeError",
    "ParkingSpot",
]
