import copy
import json
import unittest
import numpy as np
from src.compound.study import design,scenario,simulate,observe,features,perturb
from src.compound.comparison import matrix


class StudyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cfg,cls.manifest=design()
        cls.row=next(r for r in cls.manifest["runs"] if r["run_id"] in cls.manifest["development_pilot_ids"] and r["condition"]=="family_and_assistance")
        cls.result=simulate(cls.cfg,cls.row)

    def test_matched_people_positions_and_latent_draws(self):
        rows=[r for r in self.manifest["runs"] if r["block_id"]==self.row["block_id"] and r["variant"]=="main"]
        expected=None
        for row in rows:
            _,people,_,reserved,_=scenario(self.cfg,row)
            value=json.dumps([people,reserved],sort_keys=True)
            if expected is None:expected=value
            self.assertEqual(value,expected)

    def test_prefix_only_and_hidden_generator_invariance(self):
        expected=features(observe(self.result,2,self.cfg),self.cfg)
        changed=copy.deepcopy(self.result)
        changed["private_reserved_edges"]=[{"gain":999}]
        for frame in changed["frames"]:
            frame["units"]=[{"forbidden":999}]
            if frame["t"]>1.8:frame["positions"]={"999":[999,999]}
        self.assertEqual(features(observe(changed,2,self.cfg),self.cfg),expected)
        self.assertNotIn("units",observe(self.result,2,self.cfg)["frames"][0])
        self.assertEqual(set(expected),set(sum(self.cfg["features"].values(),[])))

    def test_corruption_changes_metadata_without_motion_or_duplicate_roles(self):
        observation=observe(self.result,2,self.cfg)
        before=json.dumps(observation,sort_keys=True)
        for mode in ["drop_one_each_type","rewire_one_each_type"]:
            corrupted,count=perturb(observation,mode,23)
            self.assertEqual(corrupted["frames"],observation["frames"])
            adults=[e["adult"] for e in corrupted["edges"]]
            self.assertEqual(len(adults),len(set(adults)))
            self.assertEqual(count["selected"],2)
            self.assertEqual(count["changed"],2)
        self.assertEqual(before,json.dumps(observation,sort_keys=True))

    def test_count_only_excludes_all_other_link_features(self):
        row={"features":{n:1 for n in sum(self.cfg["features"].values(),[])}}
        counts=matrix([row],self.cfg,"F_counts")[0]
        np.testing.assert_array_equal(counts[-9:],[1,1,0,0,0,0,0,0,0])
        self.assertEqual(matrix([row],self.cfg,"M").shape,(1,25))

    def test_partitions_and_manifest_sizes(self):
        runs=self.manifest["runs"]
        self.assertEqual(len(runs),240)
        self.assertEqual(len({r["run_id"] for r in runs}),240)
        self.assertEqual(sum(r["partition"]=="train" for r in runs),48)
        self.assertTrue(all(r["geometry"] in ["G1","G2"] for r in runs if r["partition"] in ["train","validation"]))
        self.assertEqual(sum(r["variant"]=="main" and r["partition"]=="held_out_geometry_test" for r in runs),96)


if __name__=="__main__":unittest.main()
