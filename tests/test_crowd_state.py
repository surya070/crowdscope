import csv
import json
import tempfile
import unittest
from pathlib import Path
from src.crowd_state import Point, Zone, snapshot, load_csv


class CrowdStateTests(unittest.TestCase):
    zones = [Zone(0,0,0,2,2),Zone(1,2,0,4,2)]

    def run_state(self, points, **kwargs):
        return snapshot(points,self.zones,1,history=1,max_gap=1,**kwargs)

    def test_empty(self):
        s=self.run_state([])
        self.assertEqual(sum(z['count'] for z in s['zones']),0)
        self.assertIsNone(s['zones'][0]['mean_speed_m_s'])

    def test_speed_density(self):
        s=self.run_state([Point('a',0,0.5,1),Point('a',1,1.5,1)])
        self.assertEqual(s['zones'][0]['density_people_m2'],0.25)
        self.assertEqual(s['occupants'][0]['mean_speed_m_s'],1)
        self.assertTrue(s['occupants'][0]['complete_history'])

    def test_stationary(self):
        s=self.run_state([Point('a',0,1,1),Point('a',1,1,1)])
        self.assertEqual(s['zones'][0]['stopped_fraction'],1)

    def test_boundary_tie_and_conservation(self):
        s=self.run_state([Point('a',1,2,1),Point('b',1,3,1)])
        self.assertEqual([z['count'] for z in s['zones']],[1,1])
        self.assertEqual(s['occupants'][0]['zone'],0)

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            self.run_state([Point('a',1,1,1)]*2)

    def test_variable_sampling_time_weighted(self):
        s=self.run_state([Point('a',0,0,1),Point('a',0.25,0,1),Point('a',1,1.5,1)])
        self.assertEqual(s['occupants'][0]['mean_speed_m_s'],1.5)
        self.assertEqual(s['occupants'][0]['stopped_time_fraction'],0.25)

    def test_gap_not_interpolated(self):
        s=snapshot([Point('a',0,0,1),Point('a',1,1,1)],self.zones,1,history=1,max_gap=0.2)
        self.assertIsNone(s['occupants'][0]['mean_speed_m_s'])
        self.assertFalse(s['occupants'][0]['complete_history'])

    def test_fragmented_identity_unknown_motion(self):
        s=self.run_state([Point('old',0,0,1),Point('new',1,1,1)])
        self.assertEqual(len(s['occupants']),1)
        self.assertIsNone(s['occupants'][0]['mean_speed_m_s'])

    def test_disappeared_not_carried_forward(self):
        self.assertEqual(len(self.run_state([Point('a',0,1,1)])['occupants']),0)

    def test_future_invariance(self):
        a=[Point('a',0,0,1),Point('a',1,1,1)]
        self.assertEqual(self.run_state(a),self.run_state(a+[Point('a',2,100,100)]))

    def test_forward_reverse(self):
        s=self.run_state([Point('a',0,1,1),Point('a',1,3,1),Point('b',0,3,1),Point('b',1,1,1)],crossing_x=2)
        self.assertEqual((s['forward_crossing_events'],s['reverse_crossing_events']),(1,1))

    def test_outside_rejected(self):
        with self.assertRaises(ValueError): self.run_state([Point('a',1,5,1)])

    def test_overlap_rejected(self):
        with self.assertRaises(ValueError): snapshot([], [Zone(0,0,0,2,2),Zone(1,1,0,3,2)],1)

    def test_nan_rejected(self):
        with self.assertRaises(ValueError): self.run_state([Point('a',1,float('nan'),1)])

    def test_unit_conversion(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'tracks.csv'
            p.write_text('person_id,time,x,y\na,1000,100,200\n')
            self.assertEqual(load_csv(p,0.01,0.001),[Point('a',1,1,2)])


if __name__=='__main__': unittest.main()
