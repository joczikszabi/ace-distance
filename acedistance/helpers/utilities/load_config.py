import os
import configparser


def loadConfig():
    # Load config data from config file
    parser = configparser.ConfigParser()
    configFilePath = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'config.ini')
    parser.read(configFilePath)

    return parser
