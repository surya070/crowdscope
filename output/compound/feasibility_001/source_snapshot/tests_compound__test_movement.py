import copy
import math
import unittest
from shapely.geometry import Point
from shapely.geometry import box
from src.compound.cases import cases, pair, single
from src.compound.movement import footprint, swept, run


class MovementTests(unittest.TestCase):
    def test_translation_reserves_intermediate_space(self):
        unit=single(1,1,"adult",.24,1,1,2,[(1,2),(5,2)])
        obstacle=Point(2,2).buffer(.1)
        self.assertFalse(footprint(unit).intersects(obstacle))
        self.assertFalse(footprint(unit,pose=(3,2,0)).intersects(obstacle))
        self.assertTrue(swept(unit,(3,2,0)).intersects(obstacle))

    def test_rotation_reserves_arc_not_just_endpoints(self):
        unit=pair(x=2,y=2)
        obstacle=Point(1.45,1.45).buffer(.03)
        self.assertFalse(footprint(unit).intersects(obstacle))
        self.assertFalse(footprint(unit,pose=(2,2,math.pi/2)).intersects(obstacle))
        self.assertTrue(swept(unit,(2,2,math.pi/2)).intersects(obstacle))

    def test_rotation_sweep_encloses_dense_intermediate_poses(self):
        unit=pair(x=2,y=2)
        sweep=swept(unit,(2,2,math.pi/2))
        for i in range(201):
            shape=footprint(unit,pose=(2,2,math.pi/2*i/200))
            self.assertTrue(sweep.buffer(1e-9).covers(shape))

    def test_duplicate_occupants_are_rejected(self):
        case=cases()[0]
        other=copy.deepcopy(case["units"][0])
        other.id=2;other.x=4
        case["units"].append(other)
        with self.assertRaisesRegex(ValueError,"Duplicate occupant"):
            run(case,.04)

    def test_simulation_blocks_tunnelling_through_stationary_occupant(self):
        moving=single(1,1,"test_fast",.24,30,1,2,[(1,2),(10,2)])
        stationary=single(2,2,"test_stationary",.24,0,2,2,[(2,2),(2,2)])
        result=run({"name":"adversarial_tunnelling","area":box(0,0,12,4),
                    "units":[moving,stationary],"exit_axis":0,"exit_plane":8,"cap_s":1},.1)
        self.assertEqual(result["exits"],{})
        self.assertEqual(result["frames"][-1]["positions"]["1"],[1,2])
        self.assertGreater(result["verification"]["blocked_moves"],0)

    def test_separate_exit_events_and_conservation_during_outflow(self):
        result=run(next(c for c in cases() if c["name"]=="attached_pair_free"),.02)
        self.assertEqual(result["initial_occupants"],2)
        self.assertLess(result["exits"]["1"],result["exits"]["2"])
        intermediate=False
        for frame in result["frames"]:
            exited=sum(t<=frame["t"]+1e-10 for t in result["exits"].values())
            self.assertEqual(len(frame["positions"])+exited,2)
            if set(frame["positions"])=={"2"}:
                intermediate=True
                self.assertEqual(frame["units"][0]["member_ids"],[1,2])
        self.assertTrue(intermediate)

    def test_inaccessible_door_retains_full_pair(self):
        case=next(c for c in cases() if c["name"]=="inaccessible_doorway")
        case["cap_s"]=10
        result=run(case,.04)
        self.assertFalse(result["complete"])
        self.assertEqual(result["exits"],{})
        self.assertEqual(result["remaining_ids"],[1,2])
        self.assertGreater(result["verification"]["blocked_moves"],0)


if __name__=="__main__":unittest.main()
