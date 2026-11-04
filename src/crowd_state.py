"""Trajectory-only crowd measurements. Standard library; no inference labels.

Rectangular zones must partition the supplied observable geometry; polygonal
walkable areas with obstacles require a future geometry adapter.
"""
from dataclasses import dataclass
from collections import defaultdict
import csv
import math


@dataclass(frozen=True)
class Point:
    person: str
    time: float
    x: float
    y: float


@dataclass(frozen=True)
class Zone:
    id: int
    xmin: float
    ymin: float
    xmax: float
    ymax: float

    @property
    def area(self):
        return (self.xmax-self.xmin)*(self.ymax-self.ymin)

    def contains(self, p):
        return self.xmin <= p.x <= self.xmax and self.ymin <= p.y <= self.ymax


def validate_points(points):
    seen = set()
    for p in points:
        if not p.person or not all(math.isfinite(v) for v in (p.time, p.x, p.y)):
            raise ValueError('Missing ID or non-finite trajectory value')
        key = (p.person, p.time)
        if key in seen:
            raise ValueError('Duplicate person/timestamp; resolve upstream')
        seen.add(key)


def load_csv(path, position_scale=1.0, time_scale=1.0):
    """Explicit scales convert source units to metres and seconds."""
    if not all(math.isfinite(v) and v > 0 for v in (position_scale, time_scale)):
        raise ValueError('Unit scales must be positive and finite')
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        if not {'person_id', 'time', 'x', 'y'} <= set(reader.fieldnames or []):
            raise ValueError('Required columns: person_id,time,x,y')
        points = [Point(r['person_id'], float(r['time'])*time_scale,
                        float(r['x'])*position_scale, float(r['y'])*position_scale) for r in reader]
    validate_points(points)
    return points


def validate_zones(zones):
    if not zones or len({z.id for z in zones}) != len(zones):
        raise ValueError('Zones need unique IDs and a nonempty geometry')
    if all(hasattr(z,'geometry') for z in zones):
        for z in zones:
            if not z.geometry.is_valid or z.geometry.is_empty or not math.isfinite(z.area) or z.area<=0:
                raise ValueError('Invalid polygon zone')
        for i,a in enumerate(zones):
            for b in zones[i+1:]:
                if a.geometry.intersection(b.geometry).area>1e-10:
                    raise ValueError('Zone interiors overlap')
        return
    for z in zones:
        if not all(math.isfinite(v) for v in (z.xmin,z.ymin,z.xmax,z.ymax)) or z.xmax <= z.xmin or z.ymax <= z.ymin:
            raise ValueError('Zone bounds must define a positive finite area')
    for i,a in enumerate(zones):
        for b in zones[i+1:]:
            if min(a.xmax,b.xmax) > max(a.xmin,b.xmin) and min(a.ymax,b.ymax) > max(a.ymin,b.ymin):
                raise ValueError('Zone interiors overlap')


def snapshot(points, zones, time, history=2.0, max_gap=0.1, crossing_x=None):
    """Exact observed snapshot; never extrapolate disappeared occupants.

    Histories include only complete adjacent segments inside [time-history,time].
    Gaps larger than max_gap break continuity. Missing history remains unknown.
    """
    points = list(points)
    validate_points(points)
    validate_zones(zones)
    if not all(math.isfinite(v) for v in (time,history,max_gap)) or history <= 0 or max_gap <= 0:
        raise ValueError('Invalid time/history/gap')
    if crossing_x is not None and not math.isfinite(crossing_x):
        raise ValueError('Invalid crossing plane')
    tracks = defaultdict(list)
    for p in points:
        if time-history <= p.time <= time:  # future positions never enter features
            tracks[p.person].append(p)
    occupants = []
    forward = reverse = 0
    for person, track in sorted(tracks.items()):
        track.sort(key=lambda p:p.time)
        segments = [(a,b) for a,b in zip(track,track[1:]) if b.time-a.time <= max_gap+1e-12]
        if crossing_x is not None:
            forward += sum(a.x < crossing_x <= b.x for a,b in segments)
            reverse += sum(b.x < crossing_x <= a.x for a,b in segments)
        current = next((p for p in track if p.time == time), None)
        if current is None:
            continue
        candidates = [z.id for z in zones if z.contains(current)]
        if not candidates:
            raise ValueError(f'Active person {person} outside observable zones')
        # Only the contiguous suffix ending at the snapshot defines current motion.
        suffix = []
        for a,b in reversed(list(zip(track,track[1:]))):
            if b.time-a.time > max_gap+1e-12:
                break
            suffix.append((a,b))
        duration = sum(b.time-a.time for a,b in suffix)
        distance = sum(math.hypot(b.x-a.x,b.y-a.y) for a,b in suffix)
        stopped = sum(b.time-a.time for a,b in suffix
                      if math.hypot(b.x-a.x,b.y-a.y)/(b.time-a.time) < 0.1)
        occupants.append(dict(person_id=person,zone=min(candidates),x=current.x,y=current.y,
                              mean_speed_m_s=distance/duration if duration else None,
                              stopped_time_fraction=stopped/duration if duration else None,
                              history_coverage=duration/history,
                              complete_history=abs(duration-history)<1e-9))
    summaries = []
    for z in sorted(zones,key=lambda z:z.id):
        people = [p for p in occupants if p['zone']==z.id]
        known = [p for p in people if p['mean_speed_m_s'] is not None]
        summaries.append(dict(zone=z.id,area_m2=z.area,count=len(people),density_people_m2=len(people)/z.area,
                              mean_speed_m_s=sum(p['mean_speed_m_s'] for p in known)/len(known) if known else None,
                              stopped_fraction=sum(p['mean_speed_m_s']<0.1 for p in known)/len(known) if known else None,
                              motion_observed_count=len(known),missing_motion_count=len(people)-len(known)))
    assert sum(z['count'] for z in summaries)==len(occupants)
    return dict(time_s=time,history_s=history,occupants=occupants,zones=summaries,
                forward_crossing_events=forward,reverse_crossing_events=reverse,
                crossing_observation='events on contiguous observed segments only; not unique-person clearance',
                snapshot_policy='exact timestamps only; absent tracks excluded, no future interpolation')
