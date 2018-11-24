import requests
import json
import pytest

url = 'http://127.0.0.1:5000/get_answer_text'

with open('faq_test.json', 'r') as inp:
    questions = eval(inp.read())


def test_sms():
    response = requests.post(url, json=json.dumps({'text': 'Could you please help me to unsubscribe from SMS notifications?'}))
    assert response.text == questions[0]['action']


def test_tariff():
    response = requests.post(url, json=json.dumps({'text': 'Could you please help me to change my card tariff?'}))
    assert response.text == questions[1]['action']


def test_block():
    response = requests.post(url, json=json.dumps({'text': 'Could you please help me to block my card?'}))
    assert response.text == questions[2]['action']


def test_time():
    response = requests.post(url, json=json.dumps({'text': 'Could you please give me an information about your working hours?'}))
    assert response.text == questions[3]['action']


def test_currency():
    response = requests.post(url, json=json.dumps({'text': 'Could you please give me an information about currency rate?'}))
    assert response.text == questions[4]['action']


def test_pin():
    response = requests.post(url, json=json.dumps({'text': 'My card was stolen! Please, block it.'}))
    assert response.text == questions[5]['action']


def test_docs():
    response = requests.post(url, json=json.dumps({'text': 'Hello! I am going to open a new account, what documents do I need?'}))
    assert response.text == questions[5]['action']
