#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import threading
import requests
import os
import subprocess as sp

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from tqdm import tqdm
import speech_recognition as sr
from voice_verification import verify_voice
from faq import make_vectorizer, get_top_answer
from gensim.models import KeyedVectors
from flask import Flask, request
from flask_cors import CORS
from sys import stderr

os.environ['NO_PROXY'] = '127.0.0.1'

URL = 'http://127.0.0.1'
conf_threshold = 0.7


############################# FLASK INIT ################################

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#########################################################################

############################ LOGGER INIT ################################

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#########################################################################

########################### MODEL INIT ##################################

print('Loading model...')

recognizer = sr.Recognizer()
# model = KeyedVectors.load_word2vec_format('backend/wiki-news-300d-1M.vec')

print('Model loaded!')

print('Reading questions...')

with open('backend/questions.json') as file:
    questions = eval(file.read())

print('Questions read!')

vectorizer = make_vectorizer(questions)

#########################################################################

@app.route('/')
def hello():
    print(json.dumps(request.json))
    return "Succ"


@app.route('/message', methods=['POST'])
def message():
    header = request.headers['Content-Type'].split(';')[0]

    if header == 'application/json':
        try:
            text_answer = request.json['text']
            curr_state = state.get()
            if curr_state.endswith('???'):
                print('Confirmation expected, but got {}'.format(text_answer), file=stderr)
            else:
                if chat_id is not None and gbot is not None:
                    gbot.send_message(chat_id=chat_id, text=text_answer)
        except KeyError:
            print('Wrong json', file=stderr)
    else:
        raise ValueError('Json required!')

    return "Succ"


@app.route('/confirmation', methods=['POST'])
def confirmation():
    header = request.headers['Content-Type'].split(';')[0]

    if header == 'application/json':
        try:
            if request.json['confirmed']:
                curr_state = state.get()
                if not curr_state.endswith('???'):
                    print('Unexpected confirmation', file=stderr)
                else:
                    state.set(curr_state[:-3])
            else:
                state.set('default_state')
        except KeyError:
            print('Wrong json', file=stderr)
    else:
        raise ValueError('Json required!')

    return "Succ"


@app.route('/verify', methods=['POST'])
def verify():
    header = request.headers['Content-Type'].split(';')[0]

    if header == 'application/json':
        try:
            userId = request.json['userId']
            curr_state = state.get()
            if not curr_state == 'auth???':
                print('Unexpected verification', file=stderr)
            else:
                ide_user, conf, all_seg = verify_voice.identify('tmp.wav', users_ids_to_identify=[userId])
                response = False
                if userId == ide_user and conf > conf_threshold:
                    response = True
                requests.post(URL, json={"verified": response})
        except KeyError:
            print('Wrong json', file=stderr)
    else:
        raise ValueError('Json required!')

    return "Succ"


class State:
    def __init__(self):
        self._state = 'default_state'

    def set(self, state):
        print('State changed from {} to {}'.format(self._state, state))
        self._state = state

    def get(self):
        return self._state

    def __eq__(self, other):
        return self._state == other

state = State()


def process_state(text):
    "We are open from 8 a.m. to 8 p.m. every day except Mondays. Sincerely yours, whatSAP bank."
    if state == 'default_state':
        requests.post(URL, json={"text_popup": "card block"})
    elif state == 'card_block':
        requests.post(URL, json={"text_popup": "card block"})
        state.set('auth???')
    elif state == 'auth':
        requests.post(URL, json={"text_popup": "auth req"})
        state.set('block???')
    elif state == 'block':
        requests.post(URL, json={"text_popup": "block"})
        state.set('default_state')
    elif state == 'worktime':
        requests.post(URL, json={"text_popup": "work time"})
        state.set('default_state')
    elif state == ('new_account'):
        requests.post(URL, json={"text_popup": "You must carry: Proof of identity and address (Passport, Voter's ID, "
                                           "Driving Licence, Aadhar card, NREGA card, PAN card) 2 recent passport-size"
                                           " colored photographs. Scincerely yours, whatSAP bank."})
        state.set('default_state')


def process_message(text):
    if state == 'default_state':
        #get_top_answer(vectorizer, model, questions, text)(state)
        state.set(text)

    process_state(text)
    requests.post(URL, json={"text": text})


def text(bot, update):
    global chat_id
    chat_id = update.message.chat_id
    global gbot
    gbot = bot

    update.message.reply_text(update.message.text)
    process_message(update.message.text)


def voice(bot, update):
    global chat_id
    chat_id = update.message.chat_id
    global gbot
    gbot = bot

    if os.path.exists("tmp.oga"):
        os.remove("tmp.oga")

    if os.path.exists("tmp.wav"):
        os.remove("tmp.wav")
    
    r = requests.get(update.message.voice.get_file()["file_path"])
    with open("tmp.oga", "wb") as handle:
        for data in tqdm(r.iter_content()):
            handle.write(data)

    command = ["ffmpeg", '-i', 'tmp.oga', 'tmp.wav']
    pipe = sp.Popen(command, stdout=sp.PIPE, bufsize=10**8)
    pipe.communicate()

    harvard = sr.AudioFile('tmp.wav')
    with harvard as source:
        audio = recognizer.record(source)

    text = recognizer.recognize_google(audio)

    update.message.reply_text(text)
    process_message(text)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


chat_id = None
gbot = None


def main():
    updater = Updater("725456790:AAEzr3Z4nJVjQNx2qp2Q5b66BIGnk_lVpLs")

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.voice, voice))

    dp.add_error_handler(error)

    updater.start_polling()

    threading.Thread(target=app.run).start()
    print('asd')
    updater.idle()


if __name__ == '__main__':
    main()
