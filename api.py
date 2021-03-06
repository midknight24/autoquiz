from datetime import datetime
from .quizzer import AutoQuizzer
from flask import Blueprint, request, redirect
from cryptography.fernet import Fernet
from .config import SECRET, SECRET_EXPIRE,NOTION_PUB

bp = Blueprint('quiz', __name__, url_prefix='/quiz')

@bp.route('/', methods=['GET'])
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
    ans_count = request.args.get('ans_count', type=int)
    fail_count = request.args.get('fail_count', type=int)
    quizzer = AutoQuizzer()
    r = quizzer.update_quiz(quiz_id, prof, can_answer, ans_count, fail_count)
    if r.status_code != 200:
        return f'Update Quiz Failed! \n {r.json()}', 500
    return redirect(f'{NOTION_PUB}/{quiz_id.replace("-", "")}')
