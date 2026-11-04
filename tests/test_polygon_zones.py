from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'.deps/recovery-r1'))
from shapely.geometry import box
from src.polygon_zones import PolygonZone,validate_partition
from src.crowd_state import Point,snapshot


class PolygonTests(unittest.TestCase):
    def test_hole_area_and_obstacle(self):
        area=box(0,0,4,4).difference(box(1,1,2,2))
        zones=[PolygonZone(0,area)]
        validate_partition(zones,area)
        self.assertEqual(zones[0].area,15)
        with self.assertRaises(ValueError):snapshot([Point('a',1,1.5,1.5)],zones,1)

    def test_shared_edge(self):
        zs=[PolygonZone(0,box(0,0,1,1)),PolygonZone(1,box(1,0,2,1))]
        validate_partition(zs,box(0,0,2,1))
        result=snapshot([Point('a',1,1,0.5)],zs,1)
        self.assertEqual([z['count'] for z in result['zones']],[1,0])

    def test_missing_coverage(self):
        with self.assertRaises(ValueError):validate_partition([PolygonZone(0,box(0,0,1,1))],box(0,0,2,1))

    def test_overlap(self):
        with self.assertRaises(ValueError):validate_partition([PolygonZone(0,box(0,0,2,1)),PolygonZone(1,box(1,0,3,1))],box(0,0,3,1))

    def test_turn_partition(self):
        from research.run_crowd_development import cases
        for case in cases():
            validate_partition(case['zones'],case['area'])
            self.assertEqual(len(case['zones']),4)


if __name__=='__main__':unittest.main()
