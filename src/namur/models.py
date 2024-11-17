"""Models for Open Data Platform of Namur."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ParkingType(str, Enum):
    """Enum representing the type of parking."""

    NORMAL = "Place normale"
    GARAGE = "Devant accès/garage"
    PMR = "PMR"
    DROP_OFF = "Dépose-minute"
    DELIVERY = "Livraison"
    POLICE = "Police"
    TAXI = "Taxi"
    CAR_SHARING = "Car-sharing"
    RECYCLING = "Recyclage"
    CAR = "Car"
    SCHOOL_BUS = "Bus scolaire"
    ELECTRIC_CAR = "Borne électrique"
    RESERVED = "Réservé"


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
    def from_json(cls: type[ParkingSpot], data: dict[str, Any]) -> ParkingSpot:
        """Return a ParkingSpot object from a JSON dictionary.

        Args:
        ----
            data: The JSON data from the API.

        Returns:
        -------
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
            created_at=datetime.strptime(
                attr.get("date_creation"),
                "%Y-%m-%d",
            ).replace(tzinfo=UTC),
            updated_at=datetime.strptime(
                data["record_timestamp"],
                "%Y-%m-%dT%H:%M:%SZ",
            ).replace(tzinfo=UTC),
        )
