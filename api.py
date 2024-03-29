from datetime import datetime
from sqlite3 import Timestamp
from .quizzer import AutoQuizzer
from flask import Blueprint, request, redirect
from cryptography.fernet import Fernet
from .config import SECRET, SECRET_EXPIRE,NOTION_PUB, WX_CORPID, CALLBACK_TOKEN, AESKEY
from .WXBizMsgCrypt.WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET
from .wechat import WXWorkAPI
from .pub_quiz import gen_token

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

@bp.route('/callback', methods=['GET', 'POST'])
def callback():
    msg_signature = request.args.get('msg_signature', type=str)
    timestamp = request.args.get('timestamp', type=str)
    nonce = request.args.get('nonce')
    echostr = request.args.get('echostr')
    sToken = CALLBACK_TOKEN
    sEncodingAES = AESKEY
    wxcpt = WXBizMsgCrypt(sToken, sEncodingAES, WX_CORPID)
    if request.method == 'GET':
        ret,sEchoStr = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echostr)
        if ret != 0:
            return str(ret)
        return sEchoStr
    elif request.method == 'POST':
        ret, sMsg = wxcpt.DecryptMsg(request.data, msg_signature, timestamp, nonce)
        if ret != 0:
            print(ret)
            return str(ret)
        xml_tree = ET.fromstring(sMsg)
        title, U = xml_tree.find("EventKey").text.split("|")
        url = U + f'&token={gen_token()}'
        response_code = xml_tree.find("ResponseCode").text
        from_username = xml_tree.find("FromUserName").text
        wx = WXWorkAPI(WXCPT=wxcpt)
        wx.update_card(title, from_username, response_code, url)
        return "ok", 200