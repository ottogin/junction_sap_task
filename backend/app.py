import json

from flask import Flask, request
from faq import make_vectorizer, get_top_answer
from gensim.models import KeyedVectors
from sys import stderr

app = Flask(__name__)

print('Loading model...', file=stderr)

#model = KeyedVectors.load_word2vec_format('wiki-news-300d-1M.vec')

print('Model loaded!', file=stderr)

print('Reading questions...', file=stderr)

with open('questions.json') as file:
    questions = eval(file.read())

print('Questions read!', file=stderr)

vectorizer = make_vectorizer(questions)


@app.route('/')
def hello():
    return "Hello World!"


@app.route('/get_answer_text', methods=['POST'])
def get_answer_text():
    print(request.json)
    return request.json
    #data = eval(request.json)['text']
    #return get_top_answer(vectorizer, model, questions, data)()


@app.route('/get_answer_voice', methods=['POST'])
def get_answer_voice():
    data = request.get_json(force=True)
    print(json.loads(data).get('voice'))
    return data

@app.route('/getAnswer', methods=['POST'])
def get_answer():
    data = request.json['text']


app.run()
