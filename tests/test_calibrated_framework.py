import unittest
from src.crowd_state import Zone
from src.crowd_framework import CrowdFramework

class Detector:
    training_prior=.1
    def __init__(self):self.calls=0
    def predict(self,positions,times):
        self.calls+=1
        assert len(positions)==len(times)==101 and abs(times[-1]-times[0]-4)<1e-8
        return dict(probability=.8,raw_score=.95,calibration_scope='fixture')

class FrameworkChecks(unittest.TestCase):
    def engine(self):
        d=Detector();e=CrowdFramework([Zone(0,-6,-1,-1,1),Zone(1,-1,-1,3,1)],d,budget=2,capacity=1)
        return e,d

    def test_prior_before_trigger_and_cached_probability(self):
        e,d=self.engine()
        for f in range(100):e.ingest_frame(f/25,[('a',-5+f/25,0)])
        self.assertEqual(d.calls,0);self.assertAlmostEqual(e.analyse()['composition']['expected_count'],.1)
        e.ingest_frame(4,[('a',-1,0)])
        s=e.analyse();self.assertEqual(d.calls,1);self.assertAlmostEqual(s['composition']['expected_count'],.8)
        # The calibrated posterior is used directly, without another Bayes update.
        self.assertEqual(s['occupants'][0]['wheelchair_probability'],.8)
        e.ingest_frame(4.04,[('a',-.96,0)]);self.assertEqual(d.calls,1)
        e.ingest_frame(4.08,[]);self.assertEqual(e.analyse()['composition']['observed_count'],0)

    def test_gap_retains_flagged_prior(self):
        e,d=self.engine()
        for f in range(101):
            if f!=50:e.ingest_frame(f/25,[('a',-5+f/25,0)])
        self.assertEqual(d.calls,0);self.assertEqual(e.analyse()['occupants'][0]['probability_source'],'training_prior')

    def test_bad_input_and_geometry_are_explicit(self):
        e,d=self.engine();e.ingest_frame(0,[('a',0,0)])
        with self.assertRaises(ValueError):e.ingest_frame(0,[('a',0,0)])
        with self.assertRaises(ValueError):e.ingest_frame(.04,[('a',0,0),('a',1,0)])

    def test_labels_not_required_for_count_conservation(self):
        e,d=self.engine();e.ingest_frame(0,[('a',-2,0),('b',0,0)])
        s=e.analyse();self.assertEqual(sum(z['count'] for z in s['zones']),2)
        self.assertAlmostEqual(sum(z['expected_count'] for z in s['zones']),.2)
        self.assertEqual(sum(s['planning']['allocation']),2)

if __name__=='__main__':unittest.main()
