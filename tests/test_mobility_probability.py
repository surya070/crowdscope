import itertools
import unittest
from src.mobility_probability import posterior, count_distribution, composition, zone_composition


class ProbabilityTests(unittest.TestCase):
    def test_bayes_primary(self):
        self.assertAlmostEqual(posterior(1,0.2,0.2),0.5)
        self.assertAlmostEqual(posterior(0,0.2,0.2),1/17)

    def test_uninformative(self):
        for bit in (0,1): self.assertAlmostEqual(posterior(bit,0.2,0.5),0.2)

    def test_perfect(self):
        for bit in (0,1): self.assertEqual(posterior(bit,0.2,0),bit)

    def test_impossible(self):
        with self.assertRaises(ValueError):posterior(1,0,0)

    def test_invalid(self):
        for p in (-0.1,1.1,float('nan')):
            with self.assertRaises(ValueError):posterior(1,p,0.2)
        with self.assertRaises(ValueError):posterior(2,0.2,0.2)

    def test_empty(self):
        self.assertEqual(count_distribution([]),[1])
        self.assertEqual(composition([])['interval'],[0,0])

    def test_analytic_pmf(self):
        for a,b in zip(count_distribution([0.2,0.8]),[0.16,0.68,0.16]):self.assertAlmostEqual(a,b)
        self.assertEqual(count_distribution([0,1,1]),[0,0,1,0])

    def test_exhaustive_pmf(self):
        ps=[0.1,0.3,0.7,0.9]
        expected=[0]*5
        for bits in itertools.product((0,1),repeat=4):
            mass=1
            for bit,p in zip(bits,ps):mass*=p if bit else 1-p
            expected[sum(bits)]+=mass
        actual=count_distribution(ps)
        for a,b in zip(actual,expected):self.assertAlmostEqual(a,b)
        self.assertAlmostEqual(sum(actual),1)
        self.assertAlmostEqual(sum(i*p for i,p in enumerate(actual)),sum(ps))

    def test_join_missing_and_extra(self):
        state={'zones':[{'zone':0},{'zone':1}], 'occupants':[{'person_id':'a','zone':0},{'person_id':'b','zone':0}]}
        result=zone_composition(state,{'a':1,'not_present':1},0.2,0.2)
        self.assertEqual(result[0]['observed_count'],2)
        self.assertAlmostEqual(result[0]['expected_count'],0.7)
        self.assertEqual(result[0]['missing_metadata_count'],1)
        self.assertEqual(result[1]['expected_count'],0)

    def test_interval_mass(self):
        s=composition([0.2]*20)
        lo,hi=s['interval']
        self.assertGreaterEqual(sum(s['pmf'][lo:hi+1]),0.9)


if __name__=='__main__':unittest.main()
