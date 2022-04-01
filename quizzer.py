from notion import NotionAPI
from config import QUIZ_PAGE_ID

def fetch_quiz():
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
    print([q['time_prio'] for q in quizzes])
    quiz = min(quizzes, key=lambda x: x['time_prio'])
    return quiz


if __name__ == '__main__':
    q = fetch_quiz()
    print(q)