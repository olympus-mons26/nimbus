"""Typed application data structures."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float
    country: str = ""
    admin1: str = ""
    timezone: str = "auto"

    @classmethod
    def from_geocoding(cls, item: dict[str, Any]) -> "Location":
        return cls(
            name=str(item["name"]),
            latitude=float(item["latitude"]),
            longitude=float(item["longitude"]),
            country=str(item.get("country", "")),
            admin1=str(item.get("admin1", "")),
            timezone=str(item.get("timezone", "auto")),
        )

    @property
    def label(self) -> str:
        parts = [self.name]
        if self.admin1 and self.admin1.casefold() != self.name.casefold():
            parts.append(self.admin1)
        if self.country:
            parts.append(self.country)
        return ", ".join(parts)
