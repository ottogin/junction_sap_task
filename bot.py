#!/usr/bin/env python
# -*- coding: utf-8 -*-

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import subprocess as sp
from tqdm import tqdm
import requests
import os
from faq import make_vectorizer, get_top_answer
from gensim.models import KeyedVectors

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

print('Loading model...')

model = KeyedVectors.load_word2vec_format('wiki-news-300d-1M.vec')

print('Model loaded!')

print('Reading questions...')

with open('questions.json') as file:
    questions = eval(file.read())

print('Questions read!')

vectorizer = make_vectorizer(questions)


def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def text(bot, update):
    update.message.reply_text(update.message.text)
    get_top_answer(vectorizer, model, questions, update.message.text)()


def voice(bot, update):
    if os.path.exists("tmp.oga"):
        os.remove("tmp.oga")

    if os.path.exists("tmp.wav"):
        os.remove("tmp.wav")
    
    r = requests.get(update.message.voice.get_file()["file_path"])
    with open("tmp.oga", "wb") as handle:
        for data in tqdm(r.iter_content()):
            handle.write(data)

    command = [ "ffmpeg",
               '-i', 'tmp.oga',
                'tmp.wav']
    pipe = sp.Popen(command, stdout = sp.PIPE, bufsize=10**8)
    pipe.communicate()

    update.message.reply_text("processing")


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    updater = Updater("725456790:AAEzr3Z4nJVjQNx2qp2Q5b66BIGnk_lVpLs")

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, text))
    dp.add_handler(MessageHandler(Filters.voice, voice))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
