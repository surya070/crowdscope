import itertools
import math
import unittest
from fractions import Fraction
from src.resource_planning import allocations,plan,realised_shortfall,request_probability


class PlanningTests(unittest.TestCase):
    def test_feasible_count(self):
        choices=list(allocations(4,6))
        self.assertEqual(len(choices),84)
        self.assertEqual(len(set(choices)),84)
        self.assertTrue(all(sum(a)==6 for a in choices))

    def test_known_demand(self):
        self.assertEqual(plan([[1,1],[]],1,2)['allocation'],(1,0))
        self.assertEqual(plan([[1,1],[]],1,2)['expected_loss'],0)

    def test_no_budget(self):
        self.assertAlmostEqual(plan([[0.2,0.3],[0.4]],0)['expected_loss'],0.9)

    def test_empty_zones_and_tie(self):
        self.assertEqual(plan([[],[]],2)['allocation'],(0,2))

    def test_scalar_demand_loss(self):
        self.assertEqual(realised_shortfall((1,2),(5,1)),3)

    def test_total_probability_request(self):
        self.assertAlmostEqual(request_probability(0.5),0.25)
        self.assertAlmostEqual(request_probability(0.7,0.1,0.1),0.1)

    def test_expected_objective_against_all_binary_outcomes(self):
        groups=[[0.1,0.8],[0.3,0.6]]
        brute=[]
        for allocation in allocations(2,1):
            value=0
            for bits in itertools.product((0,1),repeat=4):
                mass=math.prod(Fraction(str(p)) if bit else 1-Fraction(str(p)) for p,bit in zip(groups[0]+groups[1],bits))
                value+=mass*realised_shortfall(allocation,(sum(bits[:2]),sum(bits[2:])),2)
            brute.append((value,allocation))
        result=plan(groups,1,2)
        expected=min(brute)
        self.assertAlmostEqual(result['expected_loss'],expected[0])
        self.assertEqual(result['allocation'],expected[1])

    def test_distribution_differs_from_mean(self):
        groups=[[0.9],[0.45,0.45]]  # Same expected demand, different tails.
        result=plan(groups,1,1)
        self.assertEqual(result['allocation'],(1,0))
        self.assertEqual(plan(groups,1,1,mean_only=True)['allocation'],(0,1))
        self.assertAlmostEqual(result['expected_loss'],0.9)

    def test_invalid_inputs(self):
        for args in [([],1,2),([[0.1]],-1,2),([[0.1]],1,0),([[1.1]],1,2)]:
            with self.assertRaises(ValueError):plan(*args)
        with self.assertRaises(ValueError):realised_shortfall((1,),(0.5,))


if __name__=='__main__':unittest.main()
