# coding=UTF-8
from loke import LokeEventHandler
import time
import json

class TurstatusHandler(LokeEventHandler):
    # Handler to show information about next trip, and to nag user if they haven't decided yet

    def handler_version(self):
        # Handler information
        return("Turstatus")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        self.presence_rate_limit = {} # Used to avoid same user being nagged several times pr day

    def handle_message(self, event):
        # A message is recieved from Slack

        # Trigger on call to .status and return fixed data
        if event['text'] == '.status':
            attachment = [{
                "text": "Status on Project Tur 2017",
                "pretext": "Incoming message from the dark side...",
                "author_name": "Darth Vader",
                "author_icon": "http://orig14.deviantart.net/f682/f/2010/331/4/e/darth_vader_icon_64x64_by_geo_almighty-d33pmvd.png",
                "fields": [
                {
                    "title": "Confirmed",
                    "value": "<@kjonsvik>\n<@ksolheim>\n<@robert>\n<@robin>\n ",
                    "short": "false"
                },
                {
                    "title": "Declined",
                    "value": "<@lrok>\n<@silasilas>",
                    "short": "true"
                },
                {
                    "title": "On hold",
                    "value": "Anders\n<@baa>\n<@khaugen>\n<@raiom>\n<@t_lie>",
                    "short": "false"
                }
                ],
                "color": "#F35A00"
            }]
            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))
            return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        user = event['user']

        # Capture the last time a user got "book tickets"-notification
        if not user in self.presence_rate_limit:
            self.presence_rate_limit[user] = None
        if user in self.loke.config['list_travelers'] and event['presence'] == "active":
            if self.presence_rate_limit[user] == self._get_today():
                return # Have already nagged today
            self.presence_rate_limit[user] = self._get_today()
            self.loke.sc.chat_postMessage(as_user="true:", channel=config['chan_general'], text='<@%s> is alive!! Skal han booke fly mon tro?!' % user)

    def _get_today(self):
        now = time.time()
        return now - (now % (60*60*24))

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return
