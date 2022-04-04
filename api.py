from datetime import datetime
from .quizzer import AutoQuizzer
from flask import Flask, request, redirect
from cryptography.fernet import Fernet
from .config import SECRET, SECRET_EXPIRE,NOTION_PUB

app = Flask(__name__)

@app.route('/quiz', methods=['POST'])
def update_quiz():
    token = request.args.get('token', type=str)
    f = Fernet(SECRET)
    try:
        sent_time = f.decrypt(token.encode()).decode()
    except Exception:
        return 'Invalid token', 400
    sent_time = datetime.fromisoformat(sent_time)
    cur = datetime.now().astimezone()
    delta = cur - sent_time
    if delta.seconds > SECRET_EXPIRE:
        return 'Expire token', 400
    can_answer = bool(request.args.get('can_answer', type=int))
    prof = request.args.get('proficiency', type=int)
    quiz_id = request.args.get('quiz_id', type=str)
    quizzer = AutoQuizzer()
    r = quizzer.update_quiz(quiz_id, prof, can_answer)
    if r.status_code != 200:
        return f'Update Quiz Failed! \n {r.json()}', 500
    return redirect(f'{NOTION_PUB}/{quiz_id}')

