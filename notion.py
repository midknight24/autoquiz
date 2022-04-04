import json
import pytz
from .utils import nested_get
import requests
from datetime import datetime
from .config import NOTION_API_VERSION, NOTION_SECRET, NOTION_API_BASE

class NotionAPI:
    def __init__(self, token=NOTION_SECRET):
        self.s = requests.Session()
        self.s.headers["authorization"] = "Bearer " + token
        self.s.headers["Notion-Version"] = NOTION_API_VERSION
        self.baseurl = NOTION_API_BASE

    def get_block_children(self, page_id):
        url = f'{self.baseurl}/blocks/{page_id}/children'
        r = self.s.get(url)
        return r.json()

    def get_quizdbs(self, page_id):
        """
        page_id: id of the page where groups all quizzes database
        """
        page = self.get_block_children(page_id)
        dbs = []
        for obj in page.get("results", []):
            if obj.get('type') == 'child_database' and \
                obj['child_database']['title'].endswith('Quizzes'):
                dbs.append(obj['id'])
        return dbs

    def get_question(self, db_id, query=None):
        url = f'{self.baseurl}/databases/{db_id}/query'
        r = self.s.post(url, json=query).json()
        if r.get('results', []):
            return r['results'][0]

    def get_earliest_asked(self, db_id):
        query = {
            "page_size": 1,
            "sorts": [
                {
                    "property": "Next",
                    "direction": "ascending"
                }
            ]
        }
        return self.get_question(db_id, query)

    def get_earliest_never_asked(self, db_id):
        query = {
            "page_size": 1,
            "sorts": [
                {
                    "timestamp": "created_time",
                    "direction": "ascending"
                }
            ],
            "filter": {
                "property": "Next",
                "date": {
                    "is_empty": True
                }
            }
        }
        return self.get_question(db_id, query)

    def quiz_summary(self, question):
        created_time = question['created_time'][:-1]
        created_time = datetime.fromisoformat(created_time)
        created_time = pytz.UTC.localize(created_time)
        next_time = nested_get(question, 'properties.Next.date')
        if next_time:
            next_time = datetime.fromisoformat(next_time['start'])
        else:
            next_time = None
        title = nested_get(question, 'properties.Question.title')
        if title:
            title = title[0]['plain_text']
        else:
            title = 'Unknown Question'
        return {
            'id': question['id'],
            'title': title,
            'created_time':  created_time,
            'next_time': next_time,
            'proficiency': nested_get(question, 'properties.Proficiency.number'),
            'difficulty': nested_get(question, 'properties.Difficulty.select.name'),
            'time_prio': next_time if next_time else created_time
        }

    def update_quiz(self, quiz_id, proficiency, next):
        url = f'{self.baseurl}/pages/{quiz_id}'
        data = {
            "properties": {
                "Proficiency": proficiency,
                "Next": {
                    "start": next.astimezone().isoformat()
                }
            }
        }
        return self.s.patch(url, json=data)
