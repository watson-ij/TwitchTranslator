#!/usr/bin/env python3

# Chatbot based on
# https://github.com/twitchdev/chat-samples/blob/master/python/chatbot.py

import irc.bot
import random
from googletrans import Translator
from argparse import ArgumentParser
import sys
import dateutil
import dateutil.parser
import requests
import json
import time
import pytz
import traceback
import datetime


class TwitchBot(irc.bot.SingleServerIRCBot):

    def __init__(self, username, channel, oauth, lang, clientid, queue=None):
        self.queue = queue
        server = 'irc.chat.twitch.tv'
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, oauth)], username, username)
        self.channel = '#' + channel
        self.trans = Translator(service_urls=[
            'translate.google.com',
            'translate.google.co.kr',
            'translate.google.co.jp',
        ])
        self.username = username
        self.lang = lang
        self.clientid = clientid
        self.log("Initializing translate bot")
        self.log("Translating languages (from,to): ", " ".join(f"{f},{t}" for f, t in self.lang))
        self.singleLetterTranslate = {"c": "zh-CN", "j" : "ja", "k" : "ko", "e" : "en"}

    def log(self, *args):
        if self.queue is None:
            print(*args)
        else:
            self.queue.put(" ".join(str(a) for a in args))

    def on_welcome(self, c, e):
        self.log("Joining channel", self.channel[1:], "as user", self.username)
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
#        c.privmsg(self.channel, "TwitchTranslator bot by shirokumaoni joining channel!")

    def on_pubmsg(self, c, e):
        if e.arguments[0].strip().rstrip().startswith('?'): return
        source = e.source.split('!')[0]
        if source == self.username: return
        msg = e.arguments[0]
        d = self.trans.detect(msg)
        self.log('{source}: {msg} [{lang}]'.format(source=source, msg=msg, lang=d.lang))
        for f, t in self.lang:
            # None => Translate all languages to Dest
            if d.lang == f or (f is None and d.lang != t):
                tr = self.trans.translate(msg, dest=t)
                tr_msg = tr.text
                self.log(f'---> {tr_msg}')
        sys.stdout.flush()

# For argparser
def lang_pair(s):
    try:
        f, t = s.split(',')
        if f == "None":
            f = None
        return f, t
    except:
        raise argparse.ArgumentTypeError("Language pairs must be in the form <FROM>,<TO>")

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--username", dest='username', default='yasumi67', help='twitch username')
    parser.add_argument("--channel", dest='channel', default='yasumi57', help='twitch channel to join')
    parser.add_argument("--oauth", dest='oauth', default='', help='oauth password')
    parser.add_argument("--lang", dest='lang', type=lang_pair, nargs='+', help='language pairs')
    parser.add_argument("--clientid", dest='clientid', default='', help='clientid for twitch api')
    args = parser.parse_args()
    print('Starting TwitchBot')
    while True:
        try:
            bot = TwitchBot(# Required inputs
                oauth = open('secret', 'r').readlines()[0].strip() if args.oauth == '' else args.oauth,
                username = args.username,
                channel = args.channel,
                lang = args.lang,
                clientid = args.clientid
            )
            bot.start()
        except Exception as e:
            errlog = open('error.log', 'w')
            print("ERROR!!!!! Printing backtrace:", file=errlog)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback, limit=50, file=errlog)
            print(e, file=errlog)
            print()
            print("ERROR!!!!! Trying to restart.")
            errlog.close()
            break
