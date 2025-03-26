import configparser
import time

from pathlib import Path
from utils.convClient import Client

configFilePath = Path(__file__).parent / 'config' / 'dataConv_config.ini'
config=configparser.ConfigParser()
config.read(configFilePath)

manager_socket_IP='127.0.0.1'
manager_socket_PORT=config.getint('DATA_CONV_MANAGER', 'com_with_manager_port')


def manager_connect():
    client = Client(manager_socket_IP, manager_socket_PORT, 'orbital')
    client.run()
    
    tle_data, time_data, new_range = client.prep()
   
    i=0
    while True and i < 10:
        data_from_manager = client.execute()
        if data_from_manager:
            print(data_from_manager)
        i+=1


if __name__ == "__main__":
    # Load parameters
    # Start conversation with the manager
    try: 
        manager_connect()
    except Exception as e:  # Catches any other unexpected errors
        print(f"Unexpected error occurred: {e}")
    