# coding=UTF-8
import json
import re

from loke import LokeEventHandler

class BrewHandler(LokeEventHandler):
    # Handler to store information of brews

    def handler_version(self):
        # Handler information
        return("Brew")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        # Open file containing brew-information
        with open(self.loke.config['brew'], mode='r') as infile:
            self.brews = json.load(infile)

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_message(self, event):
        # A message is recieved from Slack

        # Add gravity measure to brew. Trigger on call to 
        # .brew <date> gravity add <date> <gravity>
        brewmatch = re.match(r'\.brew (\d+) gravity add (\d{4}-\d{2}-\d{2}) (1\.\d{1,3})', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                self.brews[brewmatch.group(1)]['gravity'].append([brewmatch.group(2), brewmatch.group(3)]) # Add gravity information
                self.brews[brewmatch.group(1)]['OG'] = min(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Original Gravity based on all gravities registered
                self.brews[brewmatch.group(1)]['FG'] = max(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Final Gravity based on all gravities registered
                self.brews[brewmatch.group(1)]['gravity'].sort() # Convenience
                self.brews[brewmatch.group(1)]['ABV'] = "{0:.2f} %".format((float(self.brews[brewmatch.group(1)]['OG'])-float(self.brews[brewmatch.group(1)]['FG']))*float(131.25)) # Calculate Alcohol by Volume from OG/FG
                self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Brew:*\n%s' % ('\n'.join(['%s:: %s' % (key, value) for (key, value) in self.brews[brewmatch.group(1)].items()])))
                # Save data
                with open(self.loke.config['brew'], mode='w') as outfile: 
                    json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Delete gravity measure from brew. Trigger on call to 
        # .brew <date> gravity del <date>
        brewmatch = re.match(r'\.brew (\d+) gravity del (\d{4}-\d{2}-\d{2})', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                for date in self.brews[brewmatch.group(1)]['gravity']:
                    if date[0] == brewmatch.group(2):
                        self.brews[brewmatch.group(1)]['gravity'].remove(date) # Delete gravity information
                        self.brews[brewmatch.group(1)]['OG'] = min(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Original Gravity based on all gravities registered
                        self.brews[brewmatch.group(1)]['FG'] = max(self.brews[brewmatch.group(1)]['gravity'])[1] # Calculate Final Gravity based on all gravities registered
                        self.brews[brewmatch.group(1)]['gravity'].sort() # Convenience
                        self.brews[brewmatch.group(1)]['ABV'] = "{0:.2f} %".format((float(self.brews[brewmatch.group(1)]['OG'])-float(self.brews[brewmatch.group(1)]['FG']))*float(131.25)) # Calculate Alcohol by Volume from OG/FG
                        self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Brew:*\n%s' % ('\n'.join(['%s:: %s' % (key, value) for (key, value) in self.brews[brewmatch.group(1)].items()])))
                        # Save data
                        with open(self.loke.config['brew'], mode='w') as outfile:
                            json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Add custom key/value element to brew. Trigger on call to 
        # .brew <date> add <key> <description>
        brewmatch = re.match(r'\.brew (\d+) add (\w+) (.*)', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                if brewmatch.group(2) not in self.brews[brewmatch.group(1)]:
                    self.brews[brewmatch.group(1)][brewmatch.group(2)] = brewmatch.group(3)
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Brew:*\n%s' % ('\n'.join(['%s:: %s' % (key, value) for (key, value) in self.brews[brewmatch.group(1)].items()])))
                # Save data    
                with open(self.loke.config['brew'], mode='w') as outfile:
                    json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Delete custom key/value element to brew. Trigger on call to 
        # .brew <date> del <key>
        brewmatch = re.match(r'\.brew (\d+) del (\w+)', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                if brewmatch.group(2) in self.brews[brewmatch.group(1)] and brewmatch.group(2).upper() != 'OG' and brewmatch.group(2).upper() != 'FG' and brewmatch.group(2).lower() != 'brewdate' and brewmatch.group(2).lower() != 'gravity':
                    del self.brews[brewmatch.group(1)][brewmatch.group(2)]
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Brew:*\n%s' % ('\n'.join(['%s:: %s' % (key, value) for (key, value) in self.brews[brewmatch.group(1)].items()])))
                # Save data    
                with open(self.loke.config['brew'], mode='w') as outfile:
                    json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # Show brew information. Trigger on call to 
        # .brew <date>
        brewmatch = re.match(r'\.brew (\d+)', event['text'], re.I)
        if brewmatch:
            if len(self.brews[brewmatch.group(1)]) > 0:
                self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Brew:*\n%s' % ('\n'.join(['%s:: %s' % (key, value) for (key, value) in self.brews[brewmatch.group(1)].items()])))
            return
            
        # Add new empty brew. Trigger on call to 
        # .brew add
        brewmatch = re.match(r'\.brew add', event['text'], re.I)
        if brewmatch:
            self.brews['%s' % (len(self.brews)+1)] = {}
            self.brews['%s' % (len(self.brews))]['gravity'] = []
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='Brew %s added!' % (len(self.brews)))
            # Save data
            with open(self.loke.config['brew'], mode='w') as outfile:
                json.dump(self.brews, outfile, sort_keys=True, indent=4)
            return

        # List all brew function. Trigger on call to 
        # .brew help
        brewmatch = re.match(r'\.brew help', event['text'], re.I)
        if brewmatch:
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*Available commands:*\n.brew - _list brews_\n.brew add - _add new brew_\n.brew <date> - _Show information about brew_\n.brew <date> add <key> <description> - _Add custom element to brew_\n.brew <date> del <key> - _Delete custom element from brew_\n.brew <date> gravity add <date> <gravity> - _Add measured gravity_\n.brew <date> gravity del <date> - _Delete measured gravity_')
            return

        # List all brews. Trigger on call to 
        # .brew 
        brewmatch = re.match(r'\.brew', event['text'], re.I)
        if brewmatch:
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='*List of brews:*\n%s' % ('\n'.join(['%s - %s :: %s' % (key, self.brews[key].get('brewdate', 'Unknown date'), self.brews[key].get('name', 'No Name')) for key, brew in sorted(self.brews.items(), key=lambda i: int(i[0]))])))
            return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return
