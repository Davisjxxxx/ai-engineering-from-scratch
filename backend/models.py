"""Shared Pydantic models and Mongo helpers for AgentForge Quest."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Annotated, Any, List, Optional

from bson import ObjectId
from pydantic import BaseModel, BeforeValidator, ConfigDict, Field


def _coerce_objectid(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    return v


PyObjectId = Annotated[str, BeforeValidator(_coerce_objectid)]


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def today_str() -> str:
    return now_utc().strftime("%Y-%m-%d")


class BaseDocument(BaseModel):
    model_config = ConfigDict(populate_by_name=True, arbitrary_types_allowed=True)
    id: Optional[PyObjectId] = Field(default=None, alias="_id")

    @classmethod
    def from_mongo(cls, doc: Optional[dict]):
        if not doc:
            return None
        return cls(**doc)

    def to_mongo(self) -> dict:
        data = self.model_dump(by_alias=True, exclude_none=True)
        data.pop("_id", None)
        return data


# ---------- request payloads ----------
class ProfileSettings(BaseModel):
    focus_mode_enabled: bool = False
    reduced_motion_enabled: bool = False
    sound_enabled: bool = True


class MissionCompletePayload(BaseModel):
    score: int = 100
    completed_steps: int = 0
    total_steps: int = 0


class BrainDumpCreate(BaseModel):
    content: str
    tags: List[str] = []


class AgentBuildPayload(BaseModel):
    name: str
    role: str = ""
    prompt: str = ""
    tools: List[str] = []
    memory_config: str = "none"
    scenario_id: Optional[str] = None
    live: bool = False


class ChallengeAttempt(BaseModel):
    answer: Any = None


class ReviewGrade(BaseModel):
    quality: int = 4  # 0-5 (SM-2 style)


class NotificationPrefsPayload(BaseModel):
    daily_mission_enabled: bool = True
    streak_reminder_enabled: bool = True
    review_reminder_enabled: bool = True
    boss_reminder_enabled: bool = False
    braindump_reminder_enabled: bool = False
    weekly_recap_enabled: bool = False
    daily_pattern_drill_enabled: bool = False
    resume_lab_enabled: bool = False
    capstone_progress_enabled: bool = False
    preferred_time: str = "19:00"
    push_enabled_future_flag: bool = False


class TestOutAnswersPayload(BaseModel):
    answers: List[int] = []  # selected answer index per question


class FeedbackPayload(BaseModel):
    kind: str = "other"  # confusing, too_easy, too_hard, bug, boring, helpful, fun, other
    rating: Optional[int] = None  # 1-5
    note: Optional[str] = None
    level_id: Optional[str] = None
    mission_id: Optional[str] = None
    lab_kind: Optional[str] = None  # order, select, repair
    route: Optional[str] = None  # current page/route
    user_agent: Optional[str] = None
    app_version: Optional[str] = "1.0.0"
