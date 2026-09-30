import copy
import unittest
from model import load, validate, evaluate, analyze


class DealTests(unittest.TestCase):
    def setUp(self):self.a=load()
    def test_break_even_fee_produces_zero_npv(self):
        for offer in self.a['offers']:
            o=copy.deepcopy(offer); o['total_fee']=evaluate(self.a,o)['break_even_fee']
            self.assertAlmostEqual(evaluate(self.a,o)['incremental_npv'],0)
    def test_matching_fee_equals_best_alternative(self):
        result=analyze(self.a)
        for offer,out in zip(self.a['offers'],result['offers']):
            best=max([0]+[x['incremental_npv'] for x in result['offers'] if x['name']!=out['name']])
            o=copy.deepcopy(offer); o['total_fee']=out['fee_to_match_best_alternative']
            self.assertAlmostEqual(evaluate(self.a,o)['incremental_npv'],best)
    def test_higher_baseline_hurts_exclusivity(self):
        o=self.a['offers'][0]
        self.assertLess(evaluate(self.a,o,1.3)['incremental_npv'],evaluate(self.a,o,0.7)['incremental_npv'])
    def test_zero_discount_matches_nominal(self):
        self.a['annual_discount_rate']=0
        for o in self.a['offers']:
            m=evaluate(self.a,o); self.assertAlmostEqual(m['incremental_npv'],m['incremental_undiscounted'])
    def test_winner_can_change(self):
        self.a['offers'][0]['total_fee']=80
        self.assertEqual(analyze(self.a)['recommendation'],self.a['offers'][0]['name'])
    def test_walk_away_from_bad_deals(self):
        for o in self.a['offers']:o['total_fee']=0
        self.assertEqual(analyze(self.a)['recommendation'],'No deal')
    def test_invalid_payments_rejected(self):
        self.a['offers'][0]['payment_weights'][0]=0.8
        with self.assertRaises(ValueError):validate(self.a)


if __name__=='__main__':unittest.main()
