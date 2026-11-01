"""Seven predeclared limiting cases, not prediction-study scenarios."""
import math
from shapely.geometry import box
from shapely.ops import unary_union
from .movement import Member, Unit


def single(uid,pid,profile,radius,speed,x,y,route):
    return Unit(uid,(Member(pid,profile,radius,(0,0),speed),),tuple(route),speed,x,y)


def pair(x=1.8,y=2,route=None,uid=1,client=1,helper=2):
    return Unit(uid,(Member(client,"wheelchair",.36,(0,0),1.0),
                     Member(helper,"adult",.24,(-.75,0),1.1)),
                tuple(route or [(x,y),(10,y)]),1.0,x,y)


def cases():
    room=box(0,0,12,4)
    pedestrian=single(1,1,"adult",.24,1.2,1,2,[(1,2),(10,2)])
    wheelchair=single(1,1,"wheelchair",.36,.8,1,2,[(1,2),(10,2)])
    result=[
        {"name":"single_pedestrian","area":room,"units":[pedestrian],"exit_axis":0,"exit_plane":7,
         "expected_complete":True,"analytic_s":(7+.24-1)/1.2},
        {"name":"single_wheelchair","area":room,"units":[wheelchair],"exit_axis":0,"exit_plane":7,
         "expected_complete":True,"analytic_s":(7+.36-1)/.8},
        {"name":"attached_pair_free","area":room,"units":[pair()],"exit_axis":0,"exit_plane":7,
         "expected_complete":True,"analytic_s":7+.75+.24-1.8}]
    for name,width,expected in [("accessible_doorway",1.0,True),("inaccessible_doorway",.6,False)]:
        area=unary_union([box(0,0,4,5),box(4,2.5-width/2,12,2.5+width/2)])
        case={"name":name,"area":area,"units":[pair(y=2.5)],"exit_axis":0,"exit_plane":7,"expected_complete":expected}
        if expected:
            case["analytic_s"]=7+.75+.24-1.8
        result.append(case)
    turn_area=unary_union([box(0,0,6,3),box(3.6,0,6,12)])
    omega=min(math.pi/2,1.1/.75)
    result.append({"name":"right_angle_turn","area":turn_area,
                   "units":[pair(x=1.8,y=1.5,route=[(1.8,1.5),(4.8,1.5),(4.8,11)])],
                   "exit_axis":1,"exit_plane":7,"expected_complete":True,
                   "analytic_s":3+(7+.75+.24-1.5)+math.pi/2/omega,"analytic_tolerance_steps":5})
    # Constrained single lane: no overtaking or invented route-choice mechanism.
    y=1.0
    queue=[single(1,1,"older",.24,.6,7,y,[(7,y),(18,y)]),
           single(2,2,"adult",.24,1.3,6.1,y,[(6.1,y),(18,y)]),
           pair(x=5.1,y=y,route=[(5.1,y),(18,y)],uid=3,client=3,helper=4),
           single(4,5,"adult_parent",.24,1.0,3.5,y,[(3.5,y),(18,y)]),
           single(5,6,"child",.20,1.0,2.75,y,[(2.75,y),(18,y)]),
           single(6,7,"adult",.24,1.4,1.8,y,[(1.8,y),(18,y)])]
    result.append({"name":"mixed_single_lane_queue","area":box(0,.5,20,1.5),"units":queue,
                   "exit_axis":0,"exit_plane":12,"expected_complete":True,"family_links":[(5,6)]})
    return result
