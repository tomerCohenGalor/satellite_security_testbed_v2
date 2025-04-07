import configparser
import sys

from pathlib import Path
from utils.cyberClient import Client
from utils.utils import get_value_from_config_ini


manager_socket_IP = sys.argv[1]


def manager_connect():
    """
    Establishes a connection to a manager server using a Client Class object.

    This function initializes a `Client` object with predefined parameters and starts communication
    with the manager computer serer. It retrieves attack data dictionary and the current minute, then enters a loop to
    receive and print messages from the manager, up to a maximum of X messages.

    Steps:
    1. Creates a `Client` instance with the specified IP, port, and identifier.
    2. Starts the connection with the manager computer using the client `run` method.
    3. Prepares data by calling the `prep` method and prints the retrieved attack information.
    4. Enters a loop to receive and print messages from the manager.
    5. Terminates the loop after receiving X messages or if an exit condition is met.

    Note:
    - The `manager_socket_IP` variable should be defined before calling this function.

    """
    client = Client(manager_socket_IP, 13020, "cyber")
    client.run()

    attacks, currMinute = client.prep()
    print(attacks)

    numberOfMsg = 0
    maxNumberOfMsg = 10
    while True and numberOfMsg < maxNumberOfMsg:
        data_from_manager = client.execute()

        if data_from_manager:
            print(data_from_manager)
        numberOfMsg += 1


if __name__ == "__main__":
    manager_connect()
