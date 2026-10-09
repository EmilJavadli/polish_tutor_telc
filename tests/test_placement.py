import unittest
from placement.scoring import objective_score,classify
from placement.test_bank import GRAMMAR_VOCAB
class TestPlacement(unittest.TestCase):
 def test_objective(self):
  answers={x['id']:str(x['answer']) for x in GRAMMAR_VOCAB};self.assertEqual(objective_score(GRAMMAR_VOCAB,answers),100)
 def test_a0(self):self.assertEqual(classify({'reading':10,'listening':10,'grammar_vocab':10,'writing':10,'speaking':10})['level'],'A0')
 def test_b1_gate(self):self.assertEqual(classify({'reading':80,'listening':75,'grammar_vocab':80,'writing':65,'speaking':60})['level'],'B1')
 def test_productive_gate(self):self.assertNotEqual(classify({'reading':90,'listening':90,'grammar_vocab':90,'writing':40,'speaking':40})['level'],'B1')
if __name__=='__main__':unittest.main()
