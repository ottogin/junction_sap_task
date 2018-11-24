import requests
import json

url = 'http://127.0.0.1:5000/get_answer_text'

response = requests.post(url, json=json.dumps({'text': 'Hello, what is the weather like?'}))
print(response.text)
