# coding=UTF-8

from loke import Loke
from config import config

# Import all event handles
from modules.auto_response import AutoResponseHandler
from modules.avinor import AvinorHandler
from modules.brew import BrewHandler
from modules.chartertur import CharterturHandler
from modules.seen import SeenHandler
from modules.turstatus import TurstatusHandler
from modules.weather import WeatherHandler

if __name__ == '__main__':
    loke = Loke(config).init() # Connect to Slack
    
    AutoResponseHandler(loke)
    AvinorHandler(loke)
    BrewHandler(loke)
    CharterturHandler(loke)
    SeenHandler(loke)
    TurstatusHandler(loke)
    WeatherHandler(loke)
    
    loke.loop() # Main