import unittest
from pathlib import Path
class TestSecurityContract(unittest.TestCase):
 def test_lesson_queries_are_user_scoped(self):
  source=Path('repositories/lesson_repository.py').read_text()
  self.assertIn('LessonRecord.user_id==self.user_id',source)
  self.assertIn('LessonAttempt.user_id==self.user_id',source)
 def test_google_subject_is_used(self):
  source=Path('auth/google_oidc.py').read_text();self.assertIn("getattr(st.user,'sub'",source)
if __name__=='__main__':unittest.main()
