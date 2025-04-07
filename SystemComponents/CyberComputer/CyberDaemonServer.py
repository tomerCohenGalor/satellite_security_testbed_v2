import socket
import threading
import subprocess
from utils.utils import receive_msgpack
import configparser
from pathlib import Path

configFilePath = Path(__file__).parent / "config" / "cyber_config.ini"
config = configparser.ConfigParser()
config.read(configFilePath)


def handle_client(connection):
    """
    Handles communication with a the manager computer for activating the cyber component.

    This function processes incoming messages from a client over a socket connection. It receives
    messages using `receive_msgpack`, prints the received data, and executes a subprocess
    based on the received message.

    Parameters:
    connection (socket.socket): The socket object representing the manager computer connection.

    Behavior:
    - Retrieves and prints the socket details.
    - If no data is received, the connection is closed.
    - Executes a subprocess by running `CyberSTUB.py` with an argument extracted from the data.

    Note:
    - Assumes `data[1]` contains the necessary argument for `CyberSTUB.py`.
    """
    with connection:
        print("Connected by", connection.getpeername())
        while True:
            data = receive_msgpack(connection)
            print(data)
            if not data:
                break
            subprocess.Popen(["python", "CyberSTUB.py", data[1]], shell=True)


def start_daemon():
    """
    Starts a daemon server for the cyber computer that listens for incoming connections from the manager computer.

    This function creates a TCP server using a socket, binds it to a specified host and port
    (retrieved from a configuration file), and listens for incoming connections. For each
    new connection, it create a new thread that activate the cyber component.

    Behavior:
    - Reads the server's host and port from the `config` object.
    - Creates a socket and binds it to the specified host and port.
    - Listens for client connections and starts a new thread to handle each connection.

    Note:
    - The `config` object must be properly initialized and contain `DAEMON_SERVER` settings.
    - The `handle_client` function is used to manage individual client connections.
    - Uses threading to keep the daemon server running and not crash.
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
