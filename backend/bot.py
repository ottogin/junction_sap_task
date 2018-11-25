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


conf_threshold = 0.7
chat_id_client = None
chat_id_server = None
gbot = None
verified = False
userIdClient = ""
userIdServer = ""
qualit = 4.0


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

print('Loading model...', file=stderr)

recognizer = sr.Recognizer()
model = KeyedVectors.load_word2vec_format('backend/wiki-news-300d-1M.vec')

print('Model loaded!', file=stderr)

print('Reading questions...', file=stderr)

with open('backend/questions.json') as file:
    questions = eval(file.read())

print('Questions read!', file=stderr)

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
                    gbot.send_message(chat_id=chat_id_client, text=text_answer)
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
                    process_state()
            else:
                state.set('default_state')
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


def process_state():
    global verified
    "We are open from 8 a.m. to 8 p.m. every day except Mondays. Sincerely yours, whatSAP bank."
    if state == 'default_state':
        pass
    elif state == 'card_block':
        gbot.send_message(chat_id=chat_id_server, text="PopUp Tip\n"
                                                       "It seems that client wants to block his credit card. "
                                                       "Firstly, You should start identification procedure.")
        state.set('auth???')
    elif state == 'auth':
        gbot.send_message(chat_id=chat_id_server, text="PopUp Tip\nWrite Your ID number, please.")
        state.set('auth_data???')
    elif state == 'auth_data':
        gbot.send_message(chat_id=chat_id_server, text="PopUp Tip\nDo You want to extract the information from user messages?")
        state.set('auth_verifi???')
    elif state == 'auth_verifi':
        ide_user, conf, all_seg = verify_voice.identify('tmp.wav', users_ids_to_identify=[userId])
        if userId == ide_user and conf > conf_threshold:
            verified = True
            gbot.send_message(chat_id=chat_id_server, text="PopUp Tip\nEverything is OK about this client!")
        state.set('block???')
    elif state == 'block':
        gbot.send_message(chat_id=chat_id_server,
                          text="PopUp Tip\nStart the card blocking procedure. Please, open: https://sap.com")
        state.set('default_state')
    elif state == 'worktime':
        gbot.send_message(chat_id=chat_id_server,
                          text="PopUp Tip\nWe are open from 8 am to 8 pm ever day, and will be glad to see You :)")
        state.set('default_state')
    elif state == ('new_account'):
        gbot.send_message(chat_id=chat_id_server,
                          text="PopUp Tip\nYou should bring: Proof of identity and address (Passport, Voter's ID, "
                                           "Driving Licence, Aadhar card, NREGA card, PAN card) 2 recent passport-size"
                                           " colored photographs. Scincerely yours, whatSAP bank.")
        state.set('default_state')


def process_message(text):
    if state == 'default_state':
        get_top_answer(vectorizer, model, questions, text)(state)

    process_state()
    gbot.send_message(chat_id=chat_id_server, text=text)


def emotiontoscore(emotion):
    if emotion == 'neutral':
        return 0
    if emotion == 'excited':
        return 0.4
    if emotion == 'happy':
        return 0.6
    if emotion == 'sad':
        return -0.5
    if emotion == 'fear':
        return -0.7
    return 0.2


def text(bot, update):
    global userIdClient
    global chat_id_client
    global chat_id_server
    global gbot
    gbot = bot

    if chat_id_client == "":
        chat_id_client = update.message.chat_id
    else:
        chat_id_server = update.message.chat_id

    if state == "auth_verifi???":
        userIdClient = update.message.text

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

    process_message(text)
    emotion, conf, _ = verify_voice.define_emotion_from_audio("tmp.wav")

    global qualit
    qualit += emotiontoscore(emotion) * conf


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def regular_choice(bot, update, user_data):
    text = update.message.text
    user_data['choice'] = text
    update.message.reply_text(
        'Your {}? Yes, I would love to hear about that!'.format(text.lower()))

    return TYPING_REPLY


def custom_choice(bot, update):
    update.message.reply_text('Alright, please send me the category first, '
                              'for example "Most impressive skill"')

    return TYPING_CHOICE


def main():
    updater = Updater("725456790:AAEzr3Z4nJVjQNx2qp2Q5b66BIGnk_lVpLs")

    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [RegexHandler('^(Age|Favourite colour|Number of siblings)$',
                                    regular_choice,
                                    pass_user_data=True),
                       RegexHandler('^Something else...$',
                                    custom_choice),
                       ]
        }
    )
    dp.add_handler(conv_handler)
    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.voice, voice))

    dp.add_error_handler(error)

    updater.start_polling()

    threading.Thread(target=app.run).start()
    print('asd')
    updater.idle()


if __name__ == '__main__':
    main()
