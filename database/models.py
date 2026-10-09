import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

def uid(): return uuid.uuid4()
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__='users'; __table_args__=(UniqueConstraint('provider','issuer','provider_subject'),)
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid)
    provider:Mapped[str]=mapped_column(String(30));issuer:Mapped[str]=mapped_column(String(255));provider_subject:Mapped[str]=mapped_column(String(255))
    email:Mapped[str|None]=mapped_column(String(320));display_name:Mapped[str|None]=mapped_column(String(255));picture_url:Mapped[str|None]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow);last_login_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class UserProfile(Base):
    __tablename__='user_profiles';user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),primary_key=True)
    current_cefr_level:Mapped[str]=mapped_column(String(5),default='A0');target_cefr_level:Mapped[str]=mapped_column(String(5),default='B1')
    daily_study_minutes:Mapped[int]=mapped_column(Integer,default=60);evaluation_completed:Mapped[bool]=mapped_column(Boolean,default=False)
    evaluation_completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True));current_study_plan_id:Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True))
    current_plan_position:Mapped[int]=mapped_column(Integer,default=1);current_lesson_id:Mapped[uuid.UUID|None]=mapped_column(UUID(as_uuid=True))
    skill_profile:Mapped[dict]=mapped_column(JSONB,default=dict);updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class PlacementEvaluation(Base):
    __tablename__='placement_evaluations';id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
    version:Mapped[str]=mapped_column(String(30));status:Mapped[str]=mapped_column(String(20),default='in_progress');current_section:Mapped[str]=mapped_column(String(30),default='grammar_vocab')
    responses:Mapped[dict]=mapped_column(JSONB,default=dict);scores:Mapped[dict]=mapped_column(JSONB,default=dict);strengths:Mapped[list]=mapped_column(JSONB,default=list);weaknesses:Mapped[list]=mapped_column(JSONB,default=list)
    assigned_level:Mapped[str|None]=mapped_column(String(5));confidence:Mapped[float|None]=mapped_column(Float);started_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow);completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class StudyPlan(Base):
    __tablename__='study_plans';id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True)
    evaluation_id:Mapped[uuid.UUID|None]=mapped_column(ForeignKey('placement_evaluations.id'));status:Mapped[str]=mapped_column(String(20),default='active');start_level:Mapped[str]=mapped_column(String(5));target_level:Mapped[str]=mapped_column(String(5),default='B1')
    daily_minutes:Mapped[int]=mapped_column(Integer,default=60);start_curriculum_day:Mapped[int]=mapped_column(Integer);plan_json:Mapped[dict]=mapped_column(JSONB,default=dict);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class LessonRecord(Base):
    __tablename__='lessons';__table_args__=(UniqueConstraint('user_id','curriculum_day'),)
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);curriculum_day:Mapped[int]=mapped_column(Integer)
    lesson_json:Mapped[dict]=mapped_column(JSONB);status:Mapped[str]=mapped_column(String(20),default='ready');created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow);completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
class LessonAttempt(Base):
    __tablename__='lesson_attempts';id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);lesson_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('lessons.id',ondelete='CASCADE'),index=True)
    attempt_type:Mapped[str]=mapped_column(String(30));attempt_number:Mapped[int]=mapped_column(Integer);score:Mapped[float|None]=mapped_column(Float);passed:Mapped[bool|None]=mapped_column(Boolean);payload:Mapped[dict]=mapped_column(JSONB);created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class LessonProgress(Base):
    __tablename__='lesson_progress';__table_args__=(UniqueConstraint('user_id','lesson_id'),)
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);lesson_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('lessons.id',ondelete='CASCADE'))
    state:Mapped[dict]=mapped_column(JSONB,default=dict);updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=datetime.utcnow)
class VocabularyProgress(Base):
    __tablename__='vocabulary_progress';__table_args__=(UniqueConstraint('user_id','lemma'),)
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);lemma:Mapped[str]=mapped_column(String(255));mastery_score:Mapped[float]=mapped_column(Float,default=0);exposure_count:Mapped[int]=mapped_column(Integer,default=0);correct_count:Mapped[int]=mapped_column(Integer,default=0);incorrect_count:Mapped[int]=mapped_column(Integer,default=0)
class GrammarProgress(Base):
    __tablename__='grammar_progress';__table_args__=(UniqueConstraint('user_id','grammar_id'),)
    id:Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True),primary_key=True,default=uid);user_id:Mapped[uuid.UUID]=mapped_column(ForeignKey('users.id',ondelete='CASCADE'),index=True);grammar_id:Mapped[str]=mapped_column(String(30));mastery_score:Mapped[float]=mapped_column(Float,default=0);exposure_count:Mapped[int]=mapped_column(Integer,default=0);correct_count:Mapped[int]=mapped_column(Integer,default=0);incorrect_count:Mapped[int]=mapped_column(Integer,default=0)
