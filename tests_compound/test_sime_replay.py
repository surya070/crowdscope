import unittest
import numpy as np
from shapely.geometry import box
from src.sime_replay import first_crossing,replay,metrics
class ReplayContractTests(unittest.TestCase):
 def test_interpolated_crossing_not_track_disappearance(self):
  a=np.array([[1,0,-1,0,1],[1,1,1,0,1]],float)
  self.assertAlmostEqual(first_crossing(a,0)['t'],.02)
  self.assertIsNone(first_crossing(a,2))
  a[1,1]=2
  self.assertIsNone(first_crossing(a,0))
 def test_one_agent_and_no_target_input(self):
  result=replay(box(-7,-2,5,2),[{'id':1,'t':4.,'position':[-6,0]}],{'radius':.22,'speed':1.4,'time_gap':1.},horizon=30)
  self.assertEqual(result['status'],'completed')
  self.assertAlmostEqual(result['crossings'][1],10.,delta=.04)
  self.assertEqual(result['inserted'],1);self.assertEqual(result['removed'],1)
 def test_occupied_inlet_delays_without_losing_identity(self):
  result=replay(box(-7,-2,5,2),[{'id':i,'t':0.,'position':[-6,0]} for i in [1,2]],{'radius':.22,'speed':1.4,'time_gap':1.},horizon=30)
  self.assertEqual(result['status'],'completed')
  self.assertEqual(set(result['crossings']),{1,2})
  self.assertGreater(result['admission_delay_max_s'],.2)
  self.assertLessEqual(result['max_sampled_overlap_m'],.001)
if __name__=='__main__':unittest.main()
