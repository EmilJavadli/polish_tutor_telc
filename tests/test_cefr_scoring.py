import unittest
from placement.scoring import objective_profile,classify
from placement.test_bank import GRAMMAR_VOCAB
class Tests(unittest.TestCase):
 def answers_for(self,bands):
  return {x['id']:str(x['answer']) if x['band'] in bands else '-1' for x in GRAMMAR_VOCAB}
 def test_consecutive_mastery(self):
  self.assertEqual(objective_profile(GRAMMAR_VOCAB,self.answers_for({'A2','B1'}))['level'],'A0')
  self.assertEqual(objective_profile(GRAMMAR_VOCAB,self.answers_for({'A1','A2'}))['level'],'A2')
  self.assertEqual(objective_profile(GRAMMAR_VOCAB,self.answers_for({'A1','A2','B1'}))['level'],'B1')
 def test_conservative_overall(self):
  def p(level):return {'level':level,'score':70,'confidence':.8}
  result=classify({'reading':p('B1'),'listening':p('A2'),'grammar_vocab':p('B1'),'writing':p('A2'),'speaking':p('A1')})
  self.assertEqual(result['level'],'A2')
if __name__=='__main__':unittest.main()
