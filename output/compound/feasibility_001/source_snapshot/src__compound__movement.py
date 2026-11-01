"""Prescribed-route rigid footprints with conservative swept-space reservations."""
from dataclasses import dataclass
import math
from shapely.geometry import Point
from shapely.ops import unary_union


@dataclass(frozen=True)
class Member:
    id: int
    profile: str
    radius: float
    offset: tuple = (0.0, 0.0)
    speed_ceiling: float = 1.0


@dataclass
class Unit:
    id: int
    members: tuple
    route: tuple
    speed: float
    x: float
    y: float
    angle: float = 0.0
    waypoint: int = 1
    angular_ceiling: float = math.pi / 2

    def centres(self, x=None, y=None, angle=None):
        x = self.x if x is None else x
        y = self.y if y is None else y
        a = self.angle if angle is None else angle
        c, s = math.cos(a), math.sin(a)
        return {m.id: (x+c*m.offset[0]-s*m.offset[1], y+s*m.offset[0]+c*m.offset[1]) for m in self.members}


def circle(xy, radius, resolution):
    # Shapely's ordinary buffer is inscribed. Circumscribe the actual disc.
    return Point(xy).buffer(radius / math.cos(math.pi / (4 * resolution)), quad_segs=resolution)


def footprint(unit, resolution=16, pose=None):
    centres = unit.centres(*(pose or (unit.x, unit.y, unit.angle)))
    return unary_union([circle(centres[m.id], m.radius, resolution) for m in unit.members]).convex_hull


def swept(unit, pose, resolution=16):
    x, y, angle = pose
    old = footprint(unit, resolution)
    if len(unit.members)==1 or abs(angle-unit.angle) < 1e-14:
        return old.union(footprint(unit, resolution, pose)).convex_hull
    if abs(x-unit.x)+abs(y-unit.y) > 1e-12:
        raise ValueError("Translate and rotate in separate actions")
    n = max(1, math.ceil(abs(angle-unit.angle)/math.radians(2)))
    radius = max(math.hypot(*m.offset)+m.radius/math.cos(math.pi/(4*resolution)) for m in unit.members)
    pieces = []
    prior = old
    for j in range(1, n+1):
        next_a = unit.angle+(angle-unit.angle)*j/n
        current = footprint(unit, resolution, (x,y,next_a))
        sagitta = radius*(1-math.cos(abs(angle-unit.angle)/(2*n)))
        hull = prior.union(current).convex_hull
        pieces.append(hull.buffer(sagitta+1e-12))
        prior = current
    return unary_union(pieces)


def proposal(unit, dt):
    # At most one action per tick; a completed waypoint never grants extra time.
    while unit.waypoint < len(unit.route):
        tx, ty = unit.route[unit.waypoint]
        if math.hypot(tx-unit.x, ty-unit.y) > 1e-10:
            break
        unit.waypoint += 1
    if unit.waypoint == len(unit.route):
        return None
    tx, ty = unit.route[unit.waypoint]
    dx, dy = tx-unit.x, ty-unit.y
    desired = math.atan2(dy,dx)
    difference = math.atan2(math.sin(desired-unit.angle), math.cos(desired-unit.angle))
    if len(unit.members)>1 and abs(difference)>1e-10:
        omega = unit.angular_ceiling
        for m in unit.members:
            r = math.hypot(*m.offset)
            if r:
                omega = min(omega,m.speed_ceiling/r)
        da = math.copysign(min(abs(difference),omega*dt),difference)
        return unit.x,unit.y,unit.angle+da
    distance = min(math.hypot(dx,dy), unit.speed*dt)
    return unit.x+distance*math.cos(desired),unit.y+distance*math.sin(desired),desired


def run(case, dt, resolution=16):
    import copy
    units = copy.deepcopy(case["units"])
    members = {m.id:m for u in units for m in u.members}
    if len(members)!=sum(len(u.members) for u in units):
        raise ValueError("Duplicate occupant identity")
    area = case["area"]
    shapes = {u.id:footprint(u,resolution) for u in units}
    def validate():
        for shape in shapes.values():
            if not area.buffer(1e-10).covers(shape):
                raise RuntimeError("Footprint outside geometry")
        ids = list(shapes)
        for i,a in enumerate(ids):
            for b in ids[i+1:]:
                if shapes[a].intersection(shapes[b]).area>1e-10:
                    raise RuntimeError("Footprint overlap")
    validate()
    exits, frames = {}, []
    blocked_moves = accepted_moves = turns = 0
    max_pair_error = max_speed_excess = max_family_gap = 0.0
    all_positions = {i:xy for u in units for i,xy in u.centres().items()}
    previous = dict(all_positions)
    steps = round(case.get("cap_s",40)/dt)
    axis, plane = case["exit_axis"], case["exit_plane"]
    for step in range(steps+1):
        now = round(step*dt,9)
        for u in units:
            for m in u.members:
                xy = u.centres()[m.id]
                if xy[axis]-m.radius >= plane-1e-10:
                    exits.setdefault(m.id,now)
        kept = []
        for u in units:
            if all(m.id in exits for m in u.members):
                del shapes[u.id]
            else:
                kept.append(u)
        units = kept
        all_positions = {i:xy for u in units for i,xy in u.centres().items()}
        active = {i:xy for i,xy in all_positions.items() if i not in exits}
        if len(active)+len(exits)!=len(members):
            raise RuntimeError("Occupant conservation failure")
        for u in units:
            if len(u.members)==2:
                centres = u.centres()
                actual = math.dist(*centres.values())
                expected = math.dist(u.members[0].offset,u.members[1].offset)
                max_pair_error=max(max_pair_error,abs(actual-expected))
        for i,xy in all_positions.items():
            if step and i in previous:
                excess=math.dist(xy,previous[i])/dt-members[i].speed_ceiling
                max_speed_excess=max(max_speed_excess,excess)
        for a,b in case.get("family_links",[]):
            if a in all_positions and b in all_positions:
                max_family_gap=max(max_family_gap,math.dist(all_positions[a],all_positions[b]))
        if max_pair_error>1e-9 or max_speed_excess>1e-8:
            raise RuntimeError("Attachment or member speed bound failure")
        validate()
        if step % max(1,round(.2/dt)) == 0 or not units or step==steps:
            frames.append({"t":now,"positions":{str(i):list(xy) for i,xy in active.items()},
                           "units":[{"id":u.id,"pose":[u.x,u.y,u.angle],"member_ids":[m.id for m in u.members]} for u in units]})
        if not units or step==steps:
            break
        previous=dict(all_positions)
        # Front-first priority is fixed and public, with ID ties. No future outcome.
        order=sorted(units,key=lambda u:(-min(xy[axis] for xy in u.centres().values()),u.id))
        for u in order:
            pose=proposal(u,dt)
            if pose is None:
                continue
            sweep=swept(u,pose,resolution)
            if not area.buffer(1e-10).covers(sweep) or any(sweep.intersection(other).area>1e-10 for uid,other in shapes.items() if uid!=u.id):
                blocked_moves+=1
                continue
            turns+=abs(pose[2]-u.angle)>1e-10 and len(u.members)>1
            u.x,u.y,u.angle=pose
            shapes[u.id]=footprint(u,resolution)
            accepted_moves+=1
    return {"case":case["name"],"dt_s":dt,"polygon_segments_per_quadrant":resolution,
            "initial_occupants":len(members),"exits":{str(i):t for i,t in exits.items()},
            "remaining_ids":sorted(set(members)-set(exits)),"complete":not units,
            "completion_s":max(exits.values()) if not units else None,"cap_s":case.get("cap_s",40),
            "frames":frames,"verification":{"accounting_checked_every_update":True,
            "geometry_and_overlap_checked_every_update":True,"sweeps_checked_every_accepted_move":True,
            "max_pair_separation_error_m":max_pair_error,"max_member_speed_excess_m_s":max_speed_excess,
            "max_family_gap_m":max_family_gap,"blocked_moves":blocked_moves,"accepted_moves":accepted_moves,"turn_updates":int(turns)}}
