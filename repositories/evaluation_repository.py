"""Persistence for initial placement tests and optional placement retakes."""
from datetime import datetime, timezone
from sqlalchemy import select, update
from config import PLACEMENT_VERSION
from database.models import PlacementEvaluation, StudyPlan, UserProfile
from curriculum import recommend_start_position

class EvaluationRepository:
    def __init__(self, session_factory, user_id):
        self.session_factory = session_factory
        self.user_id = user_id

    def current(self):
        with self.session_factory() as session:
            return session.scalar(select(PlacementEvaluation).where(
                PlacementEvaluation.user_id == self.user_id,
                PlacementEvaluation.status == "in_progress",
            ).order_by(PlacementEvaluation.started_at.desc()))

    def pending_review(self):
        with self.session_factory() as session:
            return session.scalar(select(PlacementEvaluation).where(
                PlacementEvaluation.user_id == self.user_id,
                PlacementEvaluation.status == "pending_review",
            ).order_by(PlacementEvaluation.completed_at.desc()))

    def latest_completed(self):
        with self.session_factory() as session:
            return session.scalar(select(PlacementEvaluation).where(
                PlacementEvaluation.user_id == self.user_id,
                PlacementEvaluation.status == "completed",
            ).order_by(PlacementEvaluation.completed_at.desc()))

    def get_or_create(self, *, mode="initial"):
        current = self.current()
        if current is not None:
            return current
        with self.session_factory() as session:
            evaluation = PlacementEvaluation(
                user_id=self.user_id,
                version=PLACEMENT_VERSION,
                status="in_progress",
                current_section="grammar_vocab",
                responses={"_mode": mode},
            )
            session.add(evaluation)
            session.commit()
            session.refresh(evaluation)
            return evaluation

    def start_retake(self):
        return self.current() or self.get_or_create(mode="retake")

    def save_section(self, evaluation_id, section, response, next_section):
        with self.session_factory() as session:
            evaluation = session.get(PlacementEvaluation, evaluation_id)
            if evaluation is None or evaluation.user_id != self.user_id:
                raise PermissionError("Placement evaluation not found.")
            responses = dict(evaluation.responses or {})
            responses[section] = response
            evaluation.responses = responses
            evaluation.current_section = next_section
            session.commit()

    def save_result(self, evaluation_id, result, *, mode):
        with self.session_factory() as session:
            evaluation = session.get(PlacementEvaluation, evaluation_id)
            if evaluation is None or evaluation.user_id != self.user_id:
                raise PermissionError("Placement evaluation not found.")
            evaluation.completed_at = datetime.now(timezone.utc)
            evaluation.scores = result["scores"]
            evaluation.assigned_level = result["level"]
            evaluation.confidence = result["confidence"]
            evaluation.strengths = result["strengths"]
            evaluation.weaknesses = result["weaknesses"]
            evaluation.status = "completed" if mode == "initial" else "pending_review"
            session.commit()
            session.refresh(evaluation)
            return evaluation

    def apply_result(self, evaluation_id, *, daily_minutes, target_level):
        with self.session_factory() as session:
            evaluation = session.get(PlacementEvaluation, evaluation_id)
            if evaluation is None or evaluation.user_id != self.user_id:
                raise PermissionError("Placement evaluation not found.")
            profile = session.get(UserProfile, self.user_id)
            if profile is None:
                raise RuntimeError("User profile was not found.")
            recommendation = recommend_start_position(
                evaluation.assigned_level or "A0",
                dict(evaluation.scores or {}),
                evaluation.confidence,
            )
            recommended_start = recommendation["day"]
            # Never move a returning learner backwards or delete completed work.
            start_day = max(profile.current_plan_position or 1, recommended_start)
            session.execute(update(StudyPlan).where(
                StudyPlan.user_id == self.user_id,
                StudyPlan.status == "active",
            ).values(status="replaced"))
            scores = dict(evaluation.scores or {})
            plan = StudyPlan(
                user_id=self.user_id,
                evaluation_id=evaluation.id,
                status="active",
                start_level=evaluation.assigned_level,
                target_level=target_level,
                daily_minutes=daily_minutes,
                start_curriculum_day=start_day,
                plan_json={
                    "strengths": list(evaluation.strengths or []),
                    "weaknesses": list(evaluation.weaknesses or []),
                    "skill_scores": scores,
                    "placement_confidence": evaluation.confidence,
                    "placement_version": evaluation.version,
                    "personalization": self._personalization_rules(scores),
                    "start_recommendation": recommendation,
                    "recommended_start_day": recommended_start,
                    "effective_start_day": start_day,
                },
            )
            session.add(plan)
            session.flush()
            profile.current_cefr_level = evaluation.assigned_level
            profile.target_cefr_level = target_level
            profile.daily_study_minutes = daily_minutes
            profile.evaluation_completed = True
            profile.evaluation_completed_at = evaluation.completed_at
            profile.current_study_plan_id = plan.id
            profile.current_plan_position = start_day
            profile.skill_profile = scores
            profile.updated_at = datetime.now(timezone.utc)
            evaluation.status = "completed"
            session.commit()
            session.refresh(plan)
            return plan

    def keep_current_plan(self, evaluation_id):
        with self.session_factory() as session:
            evaluation = session.get(PlacementEvaluation, evaluation_id)
            if evaluation is None or evaluation.user_id != self.user_id:
                raise PermissionError("Placement evaluation not found.")
            evaluation.status = "completed"
            session.commit()

    def cancel_in_progress(self):
        with self.session_factory() as session:
            evaluation = session.scalar(select(PlacementEvaluation).where(
                PlacementEvaluation.user_id == self.user_id,
                PlacementEvaluation.status == "in_progress",
            ).order_by(PlacementEvaluation.started_at.desc()))
            if evaluation is not None:
                evaluation.status = "abandoned"
                session.commit()

    @staticmethod
    def _start_day_for_level(level):
        return {"A0": 1, "A1": 29, "A2": 64, "B1": 120}.get(level or "A0", 1)

    @staticmethod
    def _personalization_rules(scores):
        return {
            "priority_skills": [k for k, v in scores.items() if v < 45],
            "maintenance_skills": [k for k, v in scores.items() if v >= 65],
            "extra_listening": scores.get("listening", 100) < 45,
            "extra_speaking": scores.get("speaking", 100) < 45,
            "extra_writing": scores.get("writing", 100) < 45,
            "extra_grammar": scores.get("grammar_vocab", 100) < 45,
        }
