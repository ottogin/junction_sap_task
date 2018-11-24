#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import subprocess as sp
from tqdm import tqdm
import requests
import os
import speech_recognition as sr
from faq import make_vectorizer, get_top_answer
from gensim.models import KeyedVectors

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

print('Loading model...')

recognizer = sr.Recognizer()
# model = KeyedVectors.load_word2vec_format('backend/wiki-news-300d-1M.vec')

print('Model loaded!')

print('Reading questions...')

with open('backend/questions.json') as file:
    questions = eval(file.read())

print('Questions read!')

vectorizer = make_vectorizer(questions)


class State:
    def __init__(self):
        self._state = 'default_state'

    def set(self, state):
        print('State changed from {} to {}'.format(self._state, state))
        self._state = state

    def __eq__(self, other):
        return self._state == other

state = State()

def process_state():
    "We are open from 8 a.m. to 8 p.m. every day except Mondays. Scincerely yours, whatSAP bank."
    if state == 'default_state':
        pass
    elif state == 'card_block':
        # Popup authentification
        state.set('auth???')
    elif state == 'auth':
        # Make popup with auth
        state.set('block???')
    elif state == 'block':
        # Make popup with block
        state.set('default_state')
    elif state == 'worktime':
        # Make popup with worktime
        state.set('worktime???')


def process_message(text):
    if state == 'default_state':
        get_top_answer(vectorizer, model, questions, text)(state)

    process_state()


def text(bot, update):
    update.message.reply_text(update.message.text)
    process_message(update.message.text)


def voice(bot, update):
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


def main():
    updater = Updater("725456790:AAEzr3Z4nJVjQNx2qp2Q5b66BIGnk_lVpLs")

    dp = updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.voice, voice))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
