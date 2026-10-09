from datetime import datetime,timezone
from sqlalchemy import select
from database.models import PlacementEvaluation,UserProfile,StudyPlan
from config import PLACEMENT_VERSION
class EvaluationRepository:
    def __init__(self,sf,user_id):self.sf=sf;self.user_id=user_id
    def current(self):
        with self.sf() as s:return s.scalar(select(PlacementEvaluation).where(PlacementEvaluation.user_id==self.user_id,PlacementEvaluation.status=='in_progress').order_by(PlacementEvaluation.started_at.desc()))
    def get_or_create(self):
        x=self.current()
        if x:return x
        with self.sf() as s:
            x=PlacementEvaluation(user_id=self.user_id,version=PLACEMENT_VERSION);s.add(x);s.commit();s.refresh(x);return x
    def save_section(self,evaluation_id,section,response,next_section):
        with self.sf() as s:
            x=s.get(PlacementEvaluation,evaluation_id);assert x and x.user_id==self.user_id
            data=dict(x.responses or {});data[section]=response;x.responses=data;x.current_section=next_section;s.commit()
    def finish(self,evaluation_id,result,daily_minutes,target_level):
        with self.sf() as s:
            x=s.get(PlacementEvaluation,evaluation_id);assert x and x.user_id==self.user_id
            x.status='completed';x.completed_at=datetime.now(timezone.utc);x.scores=result['scores'];x.assigned_level=result['level'];x.confidence=result['confidence'];x.strengths=result['strengths'];x.weaknesses=result['weaknesses']
            start_day=result['start_day']; plan=StudyPlan(user_id=self.user_id,evaluation_id=x.id,start_level=result['level'],target_level=target_level,daily_minutes=daily_minutes,start_curriculum_day=start_day,plan_json={'weaknesses':result['weaknesses'],'strengths':result['strengths']});s.add(plan);s.flush()
            p=s.get(UserProfile,self.user_id);p.current_cefr_level=result['level'];p.target_cefr_level=target_level;p.daily_study_minutes=daily_minutes;p.evaluation_completed=True;p.evaluation_completed_at=x.completed_at;p.current_study_plan_id=plan.id;p.current_plan_position=start_day;p.skill_profile=result['scores'];s.commit();return plan
