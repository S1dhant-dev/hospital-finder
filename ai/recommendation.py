from math import asin, cos, radians, sin, sqrt
from typing import Any


def _distance_km(
    latitude: float, longitude: float, target_lat: float, target_lon: float
) -> float:
    latitude_delta = radians(target_lat - latitude)
    longitude_delta = radians(target_lon - longitude)
    value = (
        sin(latitude_delta / 2) ** 2
        + cos(radians(latitude))
        * cos(radians(target_lat))
        * sin(longitude_delta / 2) ** 2
    )
    return 6371 * 2 * asin(sqrt(value))


def recommend_hospitals(
    hospitals: list[dict[str, Any]],
    *,
    lat: float | None = None,
    lon: float | None = None,
) -> list[dict[str, Any]]:
    """Rank matching hospitals by distance when available, then by rating."""
    ranked = []
    for hospital in hospitals:
        item = dict(hospital)
        distance = None
        if lat is not None and lon is not None:
            distance = _distance_km(
                lat, lon, float(item["latitude"]), float(item["longitude"])
            )
        item["distance_km"] = distance
        ranked.append(item)

    if lat is not None and lon is not None:
        ranked.sort(
            key=lambda item: (
                item["distance_km"],
                -float(item["rating"]),
                item["name"].casefold(),
            )
        )
    else:
        ranked.sort(
            key=lambda item: (-float(item["rating"]), item["name"].casefold())
        )
    return ranked
