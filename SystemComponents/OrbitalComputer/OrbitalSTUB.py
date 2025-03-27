import configparser
import sys

from pathlib import Path
from utils.convClient import Client
from utils.utils import(
    get_value_from_config_ini
)

manager_socket_IP=sys.argv[1]
manager_socket_PORT=get_value_from_config_ini('DATA_CONV_MANAGER', 'com_with_manager_port', 'int')


def manager_connect():
    client = Client(manager_socket_IP, manager_socket_PORT, 'orbital')
    client.run()
    
    tle_data, time_data, new_range = client.prep()
    print(tle_data)

    i=0
    while True and i < 10:
        data_from_manager = client.execute()
        if data_from_manager:
            print(data_from_manager)
        i+=1


if __name__ == "__main__":
    try: 
        manager_connect()
    except Exception as e:  # Catches any other unexpected errors
        print(f"Unexpected error occurred: {e}")
    