import unittest
from pathlib import Path
from research.run_planning_manifest import schedule


class EvaluationGuardTests(unittest.TestCase):
    def test_final_denied_by_default(self):
        with self.assertRaises(PermissionError):schedule('evaluation')

    def test_explicit_flag_requires_current_release(self):
        release=Path(__file__).resolve().parents[1]/'research/evaluation_release_A1.json'
        if release.exists():
            cases,seeds,replicas=schedule('evaluation',True)
            self.assertEqual(seeds,list(range(410060,410120)))
            self.assertEqual(len(cases),14)
            self.assertEqual(replicas,10)
        else:
            with self.assertRaises(PermissionError):schedule('evaluation',True)

    def test_validation_schedule_matches_frozen_design(self):
        cases,seeds,replicas=schedule('validation')
        self.assertEqual(seeds,list(range(410040,410060)))
        self.assertEqual(len(cases),14)
        self.assertEqual(replicas,10)


if __name__=='__main__':unittest.main()
