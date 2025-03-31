import configparser
import sys

from pathlib import Path
from utils.cyberClient import Client
from utils.utils import(
    get_value_from_config_ini
)


manager_socket_IP=sys.argv[1]



def manager_connect():
    client = Client(manager_socket_IP, 13020, 'cyber')
    client.run()
    
    attacks, currMinute = client.prep()
    print(attacks)

    i=0
    while True and i < 10:
        data_from_manager = client.execute()
        
        if data_from_manager:
            print(data_from_manager)
        i+=1


if __name__ == "__main__":
    manager_connect()
   