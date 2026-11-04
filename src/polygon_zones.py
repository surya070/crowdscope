"""Shapely observable geometry adapter; retains holes and usable area."""
from dataclasses import dataclass
from shapely.geometry import Point
from shapely.ops import unary_union
from src.crowd_state import validate_zones


@dataclass(frozen=True)
class PolygonZone:
    id: int
    geometry: object

    @property
    def area(self):return self.geometry.area

    def contains(self,p):return self.geometry.covers(Point(p.x,p.y))


def validate_partition(zones,observable_area):
    validate_zones(zones)
    if not observable_area.is_valid or observable_area.is_empty:
        raise ValueError('Invalid observable geometry')
    if unary_union([z.geometry for z in zones]).symmetric_difference(observable_area).area>1e-9:
        raise ValueError('Zone union must equal observable walkable geometry')
