from datetime import datetime, timedelta
from .notion import NotionAPI
from .config import QUIZ_PAGE_ID, PROFICIENCY_MAP

class AutoQuizzer:

    def fetch_quiz(self):
        n = NotionAPI()
        dbs = n.get_quizdbs(QUIZ_PAGE_ID)
        quizzes = []
        for db in dbs:

            q0 = n.get_earliest_asked(db)
            if q0:
                quizzes.append(n.quiz_summary(q0))

            q1 = n.get_earliest_never_asked(db)
            if q1:
                quizzes.append(n.quiz_summary(q1))
        quiz = min(quizzes, key=lambda x: x['time_prio'])
        return quiz

    def update_quiz(self, quiz_id, proficiency, can_answer, ans_count, fail_count):
        n = NotionAPI()
        if can_answer:
            p = min(proficiency + 1, len(PROFICIENCY_MAP) - 1)
            ans_count += 1
        else:
            p = max(proficiency - 1, 0)
            fail_count += 1
        inv = timedelta(seconds = PROFICIENCY_MAP[p])
        next = datetime.now() + inv
        return n.update_quiz(quiz_id, p, next, ans_count, fail_count)
            
        

