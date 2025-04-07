import socket
import threading
import subprocess
from utils.utils import receive_msgpack
import configparser
from pathlib import Path

# Load configuration file
configFilePath = Path(__file__).parent / "config" / "sim_config.ini"
config = configparser.ConfigParser()
config.read(configFilePath)


def handle_client(connection):
    """
    Handles an incoming connection from the manager and start the Operational component.

    Parameters:
    - connection (socket.socket): The socket object representing the client connection.

    Behavior:
    - Receives data using `receive_msgpack()`.
    - If data is received, it is printed and used to start `OperationalSTUB.py` as a subprocess.
    - If no data is received, the connection is closed.
    """
    with connection:
        print("Connected by", connection.getpeername())
        while True:
            data = receive_msgpack(connection)
            print(data)
            if not data:
                break
            subprocess.Popen(["python", "OperationalSTUB.py", data[1]], shell=True)


def start_daemon():
    """
    Starts the daemon server that listens for incoming connections from the manager.

    Behavior:
    - Reads the host and port from the configuration file.
    - Creates a TCP socket and binds it to the configured address.
    - Listens for incoming connections and spawns a new thread for each client.

    Configuration:
    - The host and port are retrieved from `sim_config.ini` under the section `DAEMON_SERVER`.
    """
    HOST = config.get("DAEMON_SERVER", "HOST")
    PORT = config.getint("DAEMON_SERVER", "PORT")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()


if __name__ == "__main__":
    start_daemon()
