"""Models for Open Data Platform of Namur."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class ParkingSpot:
    """Object representing a parking spot."""

    spot_id: str
    parking_type: str
    street: str
    longitude: float
    latitude: float
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> ParkingSpot:
        """Return a ParkingSpot object from a JSON dictionary.

        Args:
            data: The JSON data from the API.

        Returns:
            A ParkingSpot object.
        """

        attr = data["fields"]
        geo = data["geometry"]["coordinates"]
        return cls(
            spot_id=attr.get("identifiant"),
            parking_type=attr.get("type_parking"),
            street=attr.get("rue_nom"),
            longitude=geo[0],
            latitude=geo[1],
            created_at=datetime.strptime(attr.get("date_creation"), "%Y-%m-%d"),
            updated_at=datetime.strptime(
                data["record_timestamp"], "%Y-%m-%dT%H:%M:%SZ"
            ),
        )
