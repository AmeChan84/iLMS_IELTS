import datetime
from typing import List, Dict
from models import UserProfile, DailySchedule, StudyTask
import math

class IELTSScheduler:
    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.skills = ['Listening', 'Reading', 'Writing', 'Speaking']
        self.skill_weights = self._calculate_skill_weights()

    def _calculate_skill_weights(self) -> Dict[str, float]:
        gaps = {
            skill: max(0, self.profile.target_scores[skill] - self.profile.current_scores[skill])
            for skill in self.skills
        }
        total_gap = sum(gaps.values())
        if total_gap == 0:
            return {skill: 0.25 for skill in self.skills}
        return {skill: gaps[skill] / total_gap for skill in self.skills}

    def generate_timetable(self, completed_tasks: List[StudyTask] = None) -> List[DailySchedule]:
        today = datetime.date.today()
        exam_date = self.profile.exam_date
        total_days = (exam_date - today).days

        if total_days <= 0:
            return []

        # Recalculate weights if there are completed tasks
        if completed_tasks:
            self._adjust_weights_based_on_performance(completed_tasks)

        timetable = []
        for day_idx in range(total_days):
            current_date = today + datetime.timedelta(days=day_idx)
            weekday_name = current_date.strftime('%A')
            
            daily_schedule = DailySchedule(date=current_date)
            
            # Buffer Day (Review) every 7 days
            if (day_idx + 1) % 7 == 0:
                daily_schedule.is_buffer_day = True
                desc, link = self._get_task_and_resource("Spaced Repetition")
                daily_schedule.tasks.append(StudyTask(
                    id=f"review-{day_idx}",
                    skill="Review",
                    description=desc,
                    duration_hours=2.0,
                    resource_link=link
                ))
            # Mock Test every 14 days
            elif (day_idx + 1) % 14 == 0:
                desc, link = self._get_task_and_resource("Mock Test")
                daily_schedule.tasks.append(StudyTask(
                    id=f"mock-{day_idx}",
                    skill="Mock Test",
                    description=desc,
                    duration_hours=3.5,
                    resource_link=link
                ))
            else:
                available_hours = self._get_available_hours(weekday_name)
                if available_hours > 0:
                    daily_schedule.tasks = self._assign_tasks(current_date, available_hours)
            
            timetable.append(daily_schedule)
        
        return timetable

    def _adjust_weights_based_on_performance(self, completed_tasks: List[StudyTask]):
        # Analyze performance: which skills are being completed and which are not
        skill_counts = {skill: 0 for skill in self.skills}
        completed_counts = {skill: 0 for skill in self.skills}
        
        # We look at tasks in the last 7 days for current trend
        for task in completed_tasks:
            if task.skill in skill_counts:
                skill_counts[task.skill] += 1
                if task.is_completed:
                    completed_counts[task.skill] += 1
        
        # Calculate "struggle factor" - higher if tasks are missed
        struggle_factors = {}
        for skill in self.skills:
            if skill_counts[skill] > 0:
                completion_rate = completed_counts[skill] / skill_counts[skill]
                # If completion rate is low, increase weight (struggle factor > 1)
                struggle_factors[skill] = 1.0 + (1.0 - completion_rate)
            else:
                struggle_factors[skill] = 1.0
                
        # Apply struggle factors to original weights
        new_weights = {skill: self.skill_weights[skill] * struggle_factors[skill] for skill in self.skills}
        total_weight = sum(new_weights.values())
        if total_weight > 0:
            self.skill_weights = {skill: new_weights[skill] / total_weight for skill in self.skills}

    def _get_available_hours(self, weekday: str) -> float:
        times = self.profile.availability.get(weekday, [])
        if not times:
            return 0.0
        # Simple duration calculation (assuming pairs of start/end hours)
        total = 0
        for i in range(0, len(times), 2):
            if i + 1 < len(times):
                total += (times[i+1] - times[i])
        return float(total)

    def _assign_tasks(self, day: datetime.date, total_hours: float) -> List[StudyTask]:
        tasks = []
        # Distribute hours across skills based on weights
        for skill in self.skills:
            skill_hours = total_hours * self.skill_weights[skill]
            if skill_hours >= 0.5:  # At least 30 mins to bother
                desc, link = self._get_task_and_resource(skill)
                tasks.append(StudyTask(
                    id=f"{skill}-{day.isoformat()}",
                    skill=skill,
                    description=desc,
                    duration_hours=round(skill_hours, 1),
                    predicted_impact=self._calculate_impact(skill, skill_hours),
                    resource_link=link
                ))
        return tasks

    def _get_task_and_resource(self, skill: str) -> (str, str):
        # Database of tasks and curated links
        resources = {
            'Listening': [
                ("Luyện Listening Section 1 & 2 (Cambridge 18)", "https://ieltsonlinetests.com/ielts-exam-library"),
                ("Nghe chép chính tả (Dictation) bài nói TED-Ed", "https://www.ted.com/watch/ted-ed"),
                ("Luyện kỹ năng Note-taking cho Section 3", "https://www.ieltsbuddy.com/ielts-listening-test.html"),
                ("Làm Full Test Listening & phân tích lỗi sai", "https://mini-ielts.com/listening")
            ],
            'Reading': [
                ("Đọc Academic Passage 1 & Skimming kỹ thuật", "https://www.ielts-exam.net/ielts_reading/"),
                ("Luyện dạng bài Matching Headings (Cambridge 17)", "https://ieltsmaterial.com/reading/"),
                ("Học từ vựng theo chủ đề Education/Environment", "https://www.vocabulary.com/lists/ielts"),
                ("Làm Full Test Reading trong 60 phút", "https://mini-ielts.com/reading")
            ],
            'Writing': [
                ("Phân tích biểu đồ Task 1 (Line Graph/Bar Chart)", "https://ielts-simon.com/ielts-help-term-course/ielts-writing-task-1/"),
                ("Viết Body Paragraph cho Task 2 chủ đề Technology", "https://ieltsadvantage.com/writing-task-2/"),
                ("Học cấu trúc câu phức & từ nối (Cohesion)", "https://www.ieltsbuddy.com/ielts-writing-connectors.html"),
                ("Luyện viết Full Task 2 & tự chấm theo tiêu chí", "https://writeandimprove.com/")
            ],
            'Speaking': [
                ("Luyện Part 1 các chủ đề quen thuộc (Work/Study)", "https://ieltsliz.com/ielts-speaking-part-1-topics-questions/"),
                ("Nói Part 2 sử dụng kỹ thuật Mind-map", "https://www.ieltsbuddy.com/ielts-speaking-part-2.html"),
                ("Luyện Part 3: Giải thích & đưa ra ví dụ", "https://ieltsadvantage.com/ielts-speaking-part-3-guide/"),
                ("Record & nghe lại để sửa phát âm/ngữ điệu", "https://otter.ai/")
            ],
            'Spaced Repetition': [
                ("Ôn tập lại kiến thức đã học trong tuần qua", "https://ankiweb.net/about")
            ],
            'Mock Test': [
                ("Làm bài Full Mock Test để đánh giá lại năng lực", "https://ielts.idp.com/vietnam/prepare/free-practice-tests")
            ]
        }
        import random
        options = resources.get(skill, [("Luyện tập tổng hợp", "https://www.ielts.org/")])
        return random.choice(options)

    def _calculate_impact(self, skill: str, hours: float) -> float:
        # Simple mathematical model: 100 hours of focused study ~ +1.0 band score
        # Adjusted by focus level (1-5)
        base_rate = 0.01  # +0.01 band score per hour
        focus_multiplier = 0.5 + (self.profile.focus_level / 5.0)
        return hours * base_rate * focus_multiplier
