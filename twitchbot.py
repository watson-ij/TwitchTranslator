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
        c.privmsg(self.channel, "TwitchTranslator bot by shirokumaoni joining channel!")

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            self.log('Received command: ' + cmd)
            self.do_command(e, cmd)
        elif e.arguments[0][0] in "cejk" and e.arguments[0][1] == ' ':
            source = e.source.split('!')[0]
            to = self.singleLetterTranslate[e.arguments[0][0]]
            msg = e.arguments[0][2:]
            self.log('Recieved message: "', msg, ' to be translated to ', to)
            tr = self.trans.translate(msg, dest=to)
            c.privmsg(self.channel, f"{tr.text} @{source}")
            self.log(f'Translated message to {to}: {tr.text}')
        else:
            if e.arguments[0].strip().rstrip().startswith('?'): return
            source = e.source.split('!')[0]
            if source == self.username: return
            msg = e.arguments[0]
            d = self.trans.detect(msg)
            self.log('Recieved message: "', msg, '" from ', source, " in language ", d.lang)
            for f, t in self.lang:
                if d.lang == f:
                    tr = self.trans.translate(msg, dest=t)
                    tr_msg = tr.text
                    c.privmsg(self.channel, f"{tr_msg} @{source}")
                    self.log(f'Translated message to {t}: {tr_msg}')
            sys.stdout.flush()
        return

    def do_command(self, e, cmd):
        c = self.connection
        self.log(cmd)
        if cmd == "dice":
            self.log("a game of dice?")
            c.privmsg(self.channel, "You rolled a %d" % random.randint(1, 6))
        elif cmd == "help":
            c.privmsg(self.channel, "Hello, I'm the TranslateBot, made for yasumi57. I am currently translating: %s. If you start a message with a letter and space, I will translate to a particular language: %s. I also know the commands: !dice, !uptime, !help." % (", ".join(f"from {f} to {t}" for f, t in self.lang), ", ".join(f"{c} to {lang}" for c, lang in self.singleLetterTranslate.items())))
        elif cmd == "uptime":
            url = f'https://api.twitch.tv/kraken/streams/{self.channel[1:]}'
            self.log("getting uptime @", url)
            r = requests.get(url=url, headers={"Client-ID": self.clientid})
            res = json.loads(r.text)
            self.log(res)
            if res['stream'] is None:
                c.privmsg(self.channel, "Stream uptime: I haven't started streaming!")
            else:
                start = dateutil.parser.parse(res['stream']['created_at'])
                now = datetime.datetime.now(pytz.timezone('UTC'))
                delta = dateutil.relativedelta.relativedelta(now, start)
                c.privmsg(self.channel, f"Stream uptime: {delta.hours}:{delta.minutes}")
        else:
            self.log(self.channel, "I don't know what "+cmd+" means")

# For argparser
def lang_pair(s):
    try:
        f, t = s.split(',')
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
