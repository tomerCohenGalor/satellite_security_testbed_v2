import socket
import threading
import subprocess
from utils.utils import receive_msgpack
import configparser
from pathlib import Path

# Load configuration file
configFilePath = Path(__file__).parent / 'config' / 'dataConv_config.ini'
config=configparser.ConfigParser()
config.read(configFilePath)

# Retrieve daemon server configuration
HOST=config.get('DAEMON_SERVER', 'daemon_IP') 
PORT=config.get('DAEMON_SERVER', 'daemon_PORT')

def handle_client(connection):
    """
    Handles communication with a connected manager "client".

    Args:
        connection (socket.socket): The client connection socket.
    """
    with connection:
        print('Connected by', connection.getpeername())
        while True:
            data = receive_msgpack(connection)
            print("me", data)
            
            if not data:
                break
                
            print("manager run")
            manager_comp_IP=data[1]
            subprocess.Popen(["python", "OrbitalSTUB.py", manager_comp_IP], shell=True)

def start_daemon():
    """
    Starts the daemon server that listens for incoming client connections from the manager computer.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, int(PORT)))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    start_daemon()
