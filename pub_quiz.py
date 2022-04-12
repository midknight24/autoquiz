from .config import API_URL, SECRET
from datetime import datetime
from .wechat import WXWorkAPI
from .quizzer import AutoQuizzer
from cryptography.fernet import Fernet


def gen_token():
    f = Fernet(SECRET)
    time = datetime.now().astimezone()
    return f.encrypt(time.isoformat().encode()).decode()


def format_quiz(quiz):
    return f"""Quiz: {quiz['title']}
难度：{quiz['difficulty']} | 当前熟练度：p{quiz['proficiency']}
能答：{quiz['answer_count']}次 | 不懂：{quiz['fail_count']}次"""

def format_button(quiz, can_answer):
    token = gen_token()
    return f"{API_URL}/quiz?token={token}&quiz_id={quiz['id']}&proficiency={quiz['proficiency']}&can_answer={int(can_answer)}&ans_count={quiz['answer_count']}&fail_count={quiz['fail_count']}"

def format_interaction(quiz):
    can_answer = format_button(quiz, True)
    fail = format_button(quiz, False)
    return f"<a href=\"{can_answer}\">懂</a>            <a href=\"{fail}\">不懂</a>"


aq = AutoQuizzer()
wx = WXWorkAPI()
q = aq.fetch_quiz()
msg = f'{format_quiz(q)}\n{format_interaction(q)}'
wx.send_msg(msg)

