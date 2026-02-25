from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Dict, Optional

@dataclass
class UserProfile:
    current_scores: Dict[str, float]  # {'Listening': 6.0, 'Reading': 6.5, ...}
    target_scores: Dict[str, float]
    exam_date: date
    availability: Dict[str, List[int]]  # {'Monday': [18, 20], 'Saturday': [8, 12, 14, 18], ...}
    focus_level: int  # 1-5
    learning_style: str  # 'Visual', 'Auditory', 'Kinesthetic', 'Read/Write'

@dataclass
class StudyTask:
    id: str
    skill: str
    description: str
    duration_hours: float
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    predicted_impact: float = 0.0  # Estimated band score increase
    resource_link: Optional[str] = None  # Link to PDF, Video, or Article
    study_guide: Optional[str] = None  # Specific instructions on how to learn

@dataclass
class DailySchedule:
    date: date
    tasks: List[StudyTask] = field(default_factory=list)
    is_buffer_day: bool = False

@dataclass
class LearningLog:
    logs: List[StudyTask] = field(default_factory=list)

    def add_task(self, task: StudyTask):
        self.logs.append(task)

    def get_progress_data(self):
        # Logic to calculate progress over time
        pass
