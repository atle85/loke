import xml.etree.ElementTree
import sqlite3
import os
import time
import re
#from urllib import urlretrieve
import urllib.request 
from datetime import datetime
import dateutil.parser
from dateutil import tz

from loke import LokeEventHandler

class AvinorHandler(LokeEventHandler):
    def handler_version(self):
        return("Avinor")

    def __init__(self, loke):
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: Avinor")

    def handle_message(self, event):
        avinormatch = re.match(r'\.avinor (.*) (.*) (.*)', event['text'], re.I)
        if avinormatch:
            flight = Flight(avinormatch.group(1), avinormatch.group(2), avinormatch.group(3))
            if flight:
                if flight.arrdep == 'D':
                    message = "*Flight: %s (%s)*\n%s (%s) - %s (%s)\nTime: %s\nStatus: %s - %s\nGate: %s" % (flight.flightno, flight.airlinename, flight.localairport.name, flight.localairport.code, flight.remoteairport.name, flight.remoteairport.code, datetime.strftime(flight.schedule_time, '%H:%M'), getattr(flight, 'statusname', 'No status available'), datetime.strftime(getattr(flight, 'statustime', flight.schedule_time), '%H:%M'), flight.gate)
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=message)
                else:
                    message = "*Flight: %s (%s)*\n%s (%s) - %s (%s)\nTime: %s\nStatus: %s - %s\nBelt: %s" % (flight.flightno, flight.airlinename, flight.remoteairport.name, flight.remoteairport.code, flight.localairport.name, flight.localairport.code, datetime.strftime(flight.schedule_time, '%H:%M'), getattr(flight, 'statusname', 'No status available'), datetime.strftime(getattr(flight, 'statustime', flight.schedule_time), '%H:%M'), flight.belt)
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=message)
            return

    def handle_presence_change(self, event):
        return


class Airport:
    def __init__(self, localairport):
        update_cache()

        self.code = localairport
        self.airports = {}

        if not os.path.isfile('cache/avinor_%s.xml' % localairport):
            urllib.request.urlretrieve('http://flydata.avinor.no/XmlFeed.asp?TimeFrom=48&TimeTo=72&airport=%s' % localairport, 'cache/avinor_%s.xml' % localairport)
        else:
            td = datetime.now() - datetime.fromtimestamp(os.path.getmtime('cache/avinor_%s.xml' % localairport))
            if td.seconds > 600:
                urllib.request.urlretrieve('http://flydata.avinor.no/XmlFeed.asp?TimeFrom=48&TimeTo=72&airport=%s' % localairport, 'cache/avinor_%s.xml' % localairport)

        # airports
        e = xml.etree.ElementTree.parse('cache/avinor_airports.xml').getroot()
        for airport in e:
            self.airports[airport.get('code')] = airport.get('name')

        self.name = self.airports[self.code]
        self.flightdata = xml.etree.ElementTree.parse('cache/avinor_%s.xml' % localairport).getroot()

class Flight:
    def __init__(self, airport, flightno, date):
        update_cache()

        # All times are in zulu, need conversion
        to_zone = tz.gettz('Europe/Oslo')
        self.airport = Airport(airport)

        self.statuses = {}
        self.airlines = {}

        self.flightno = ''
        self.belt = ''
        self.gate = ''

        # Statuses 
        e = xml.etree.ElementTree.parse('cache/avinor_statuses.xml').getroot()
        for status in e:
            self.statuses[status.get('code')] = status.get('statusTextNo')

        # Airlines
        e = xml.etree.ElementTree.parse('cache/avinor_airlines.xml').getroot()
        for airline in e:
            self.airlines[airline.get('code')] = airline.get('name')

        # Check XML for flight number entry
        for flight in self.airport.flightdata[0].findall('flight'):
            flightdate = dateutil.parser.parse(flight.find('schedule_time').text).astimezone(to_zone)
            if flight.find('flight_id').text == flightno and date == datetime.strftime(flightdate, "%Y-%m-%d"):
                self.airline = flight.find('airline').text
                self.airlinename = self.airlines[self.airline]
                self.domint = flight.find('dom_int').text
                self.flightno = flight.find('flight_id').text
                self.localairport = Airport(airport)
                self.remoteairport = Airport(flight.find('airport').text)
                print(flight)
                self.arrdep = flight.find('arr_dep').text
                self.schedule_time = flightdate
                if flight.find('belt') is not None:
                    self.belt = flight.find('belt').text

                if flight.find('gate') is not None:
                    self.gate = flight.find('gate').text

                for status in flight.iter('status'):
                    self.status = status.get('code')
                    self.statusname = self.statuses[self.status]

                    if self.status == 'A' or self.status == 'D' or self.status == 'E':
                        self.statustime = dateutil.parser.parse(status.get('time')).astimezone(to_zone)
       
       # ## Code to be used if cached version of avinor data is available - currently not a part of loke project
       # if self.flightno == '':
       #     # Entry not found in XML, check database
       #     conn = sqlite3.connect('/home/chriskj/python/avinor.sqlite3')
       #     conn.row_factory = sqlite3.Row
       #     t = (airport, flightno, date, )
       #     c = conn.cursor()
       #     c.execute('select * from flightstatus where homeairport=? and flightId=? and date(schedule_time) = ? order by timestamp desc', t)
       #     entry = c.fetchone()
       #     if entry is not None:
       #         self.airline = entry['airline']
       #         self.airlinename = self.airlines[self.airline]
       #         self.domint = entry['dom_int']
       #         self.flightno = entry['flightId']
       #         self.localairport = Airport(entry['homeairport'])
       #         self.remoteairport = Airport(entry['airport'])
       #         self.arrdep = entry['arr_dep']
       #         self.schedule_time = dateutil.parser.parse(entry['schedule_time']).astimezone(to_zone)
       #         self.status = entry['status_code']
       #         self.statusname = self.statuses[self.status]
       #         if self.status == 'A' or self.status == 'D' or self.status == 'E':
       #             self.statustime = dateutil.parser.parse(entry['status_time']).astimezone(to_zone)
       #         self.belt = entry['belt_number']

def update_cache():
    # Check if cache directory exists
    if not os.path.exists('cache'):
        os.makedirs('cache')
    
    # Update files if they are too old
    if not os.path.isfile('cache/avinor_airlines.xml'):
        urllib.request.urlretrieve('http://flydata.avinor.no/airlineNames.asp', 'cache/avinor_airlines.xml')
    else:
        td = datetime.now() - datetime.fromtimestamp(os.path.getmtime('cache/avinor_airlines.xml'))
        if td.seconds > 86400:
            urllib.request.urlretrieve('http://flydata.avinor.no/airlineNames.asp', 'cache/avinor_airlines.xml')
        
    if not os.path.isfile('cache/avinor_statuses.xml'):
        urllib.request.urlretrieve('http://flydata.avinor.no/flightStatuses.asp', 'cache/avinor_statuses.xml')
    else:
        td = datetime.now() - datetime.fromtimestamp(os.path.getmtime('cache/avinor_statuses.xml'))
        if td.seconds > 86400:
            urllib.request.urlretrieve('http://flydata.avinor.no/flightStatuses.asp', 'cache/avinor_statuses.xml')
    
    if not os.path.isfile('cache/avinor_airports.xml'):
            urllib.request.urlretrieve('http://flydata.avinor.no/airportNames.asp', 'cache/avinor_airports.xml')
    else:
        td = datetime.now() - datetime.fromtimestamp(os.path.getmtime('cache/avinor_airports.xml'))
        if td.seconds > 86400:
            urllib.request.urlretrieve('http://flydata.avinor.no/airportNames.asp', 'cache/avinor_airports.xml')


