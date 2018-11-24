import requests
import json
import pytest

url = 'http://127.0.0.1:5000/get_answer_text'

with open('questions.json', 'r') as inp:
    questions = eval(inp.read())


response = requests.post(url, json=json.dumps({'text': 'Could you please help me to unsubscribe from SMS notifications'}))
assert response.text == questions[0]['action']()


response = requests.post(url, json=json.dumps({'text': 'Could you please help me to change my tariff'}))
assert response.text == questions[1]['action']()


response = requests.post(url, json=json.dumps({'text': 'Change my tariff'}))
assert response.text == questions[1]['action']()


response = requests.post(url, json=json.dumps({'text': 'Could you change my tariff'}))
assert response.text == questions[1]['action']()


response = requests.post(url, json=json.dumps({'text': 'Could you please help me to block my card?'}))
assert response.text == questions[2]['action']()


response = requests.post(url, json=json.dumps({'text': 'Could you please give me an information about your working hours'}))
assert response.text == questions[3]['action']()


response = requests.post(url, json=json.dumps({'text': 'What is current exchange rate for dollar'}))
assert response.text == questions[4]['action']()


response = requests.post(url, json=json.dumps({'text': 'Help me please to change PIN code of my card'}))
assert response.text == questions[5]['action']()

response = requests.post(url, json=json.dumps({'text': 'Hello! I am going to open a new account, what documents do I need'}))
assert response.text == questions[6]['action']()

response = requests.post(url, json=json.dumps({'text': 'I want to open new account'}))
assert response.text == questions[6]['action']()
