import configparser
import sys

from pathlib import Path
from utils.rubySatClient import Client
from utils.utils import(
    get_value_from_config_ini
)
from utils.OperationalResEx import (
    cosmosData,
    command,
    commandAndCosmos
    )
import random

manager_socket_IP=sys.argv[1]
manager_socket_PORT=get_value_from_config_ini('MANAGER_COM', 'manager_client_PORT', 'int')


def manager_connect():
    client = Client(manager_socket_IP, manager_socket_PORT, 'operational')
    client.run()
    
    tle_data, time_data, night_probability = client.prep()

    i=0
    while True and i < 20:
        if i % 3 == 0:
            data_from_manager = client.execute(random.choice([cosmosData, command, commandAndCosmos]))
        else:
            data_from_manager = client.execute()
        
        if data_from_manager:
            print(data_from_manager)
        i+=1


if __name__ == "__main__":
    manager_connect()
   