# coding=UTF-8

# Import core
from loke import Loke
from config import config

# Import all event handles - comment out the ones you don't need.
# Please note that some of them requires files in data/ to be present
from modules.atb import AtBHandler
from modules.auto_response import AutoResponseHandler
from modules.avinor import AvinorHandler
from modules.brew import BrewHandler
from modules.bysykkel import BysykkelHandler
from modules.chartertur import CharterturHandler
from modules.mannen import MannenHandler
from modules.ruter import RuterHandler
from modules.seen import SeenHandler
from modules.tfl import TfLHandler
from modules.turstatus import TurstatusHandler
from modules.yr import YrHandler
from modules.weather import WeatherHandler

if __name__ == '__main__':
    loke = Loke(config).init() # Connect to Slack
    
    AtBHandler(loke)
    AutoResponseHandler(loke)
    AvinorHandler(loke)
    BrewHandler(loke)
    BysykkelHandler(loke)
    CharterturHandler(loke)
    MannenHandler(loke)
    RuterHandler(loke)
    SeenHandler(loke)
    TfLHandler(loke)
    TurstatusHandler(loke)
    YrHandler(loke)
    WeatherHandler(loke)

    loke.loop() # Main
