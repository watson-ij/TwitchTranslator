#!/usr/bin/env python3

# Chatbot based on
# https://github.com/twitchdev/chat-samples/blob/master/python/chatbot.py

import irc.bot
import random
from googletrans import Translator

# Required inputs
oauth = open('secret', 'r').readlines()[0].strip()
username = 'yasumi67'
channel = 'yasumi57'

class TwitchBot(irc.bot.SingleServerIRCBot):

    def __init__(self):
        server = 'irc.chat.twitch.tv'
        port = 6667
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, oauth)], username, username)
        self.channel = '#' + channel
        self.trans = Translator(service_urls=[
            # 'translate.google.com',
            'translate.google.co.kr',
        ])

    def on_welcome(self, c, e):
        print("Joining channel: ", self.channel)
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        c.privmsg(self.channel, "TwitchTranslator bot by shirokumaoni joining channel!")

    def on_pubmsg(self, c, e):
        # If a chat message starts with an exclamation point, try to run it as a command
        if e.arguments[0][:1] == '!':
            cmd = e.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(e, cmd)
        else:
            if e.arguments[0].strip().rstrip().startswith('?'): return
            d = self.trans.detect(e.arguments[0])
            src = ''
            if d.lang == "ja": src = 'ko'
            elif d.lang == "ko": src = 'ja'
            elif d.lang == "en": src = 'ko'
            if src == '': 
                print(f"Unknown language {src}")
                return
            t = self.trans.translate(e.arguments[0], dest=src)
            source = e.source.split('!')[0]
            c.privmsg(self.channel, f"{t.text} @{source}") #  https://bit.ly/2JkMBmb")
            print('Recieved message: "', e.arguments[0], '" from ', source, " in language ", d.lang)
            print('Translated message: ', t.text)
        return

    def do_command(self, e, cmd):
        c = self.connection
        print(cmd)
        if cmd == "dice":
            print("dice?")
            c.privmsg(self.channel, "You rolled a %d" % random.randint(1, 6))
        else:
            print(self.channel, "I dunno what "+cmd+" means")

if __name__ == "__main__":
  while True:
    try:
        bot = TwitchBot()
        bot.start()
    except Exception as e:
        print("ERROR!!!!! Printing backtrace:")
        print()
        print(e)
        print()
        print("ERROR!!!!! Trying to restart.")