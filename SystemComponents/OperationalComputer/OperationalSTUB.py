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


# Retrieve manager socket IP and port from command-line arguments and configuration file
manager_socket_IP=sys.argv[1]
manager_socket_PORT=get_value_from_config_ini('MANAGER_COM', 'manager_client_PORT', 'int')


def manager_connect():
    """
    Establishes a connection with the manager using the Client class and runs in a loop.

    - Creates a `Client` instance with the given manager socket IP and port.
    - Initiates the client run process.
    - Prepares necessary telemetry data.
    - Iterates up to maxNumberOfMsg times, executing commands at random intervals:
      - Every third iteration executes a random command from `cosmosData`, `command`, or `commandAndCosmos`.
      - Otherwise, executes a default command.
    - Prints any received data from the manager.
    """
    client = Client(manager_socket_IP, manager_socket_PORT, 'operational')
    client.run()
    
    tle_data, time_data, night_probability = client.prep()

    i=0
    maxNumberOfMsg=20
    while True and i < maxNumberOfMsg:
        if i % 3 == 0:
            data_from_manager = client.execute(random.choice([cosmosData, command, commandAndCosmos]))
        else:
            data_from_manager = client.execute()
        
        if data_from_manager:
            print(data_from_manager)
        i+=1


if __name__ == "__main__":
    manager_connect()
   