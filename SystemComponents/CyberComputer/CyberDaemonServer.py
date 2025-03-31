import socket
import threading
import subprocess
from utils.utils import(receive_msgpack)
import configparser
from pathlib import Path

configFilePath = Path(__file__).parent / 'config' / 'cyber_config.ini'
config=configparser.ConfigParser()
config.read(configFilePath)


def handle_client(connection):
    with connection:
        print('Connected by', connection.getpeername())
        while True:
            data = receive_msgpack(connection)
            print(data)
            if not data:
                break
            subprocess.Popen(["python", "CyberSTUB.py", data[1]], shell=True)

def start_daemon():
    HOST=config.get('DAEMON_SERVER', 'HOST')
    PORT=config.getint('DAEMON_SERVER', 'PORT')
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            threading.Thread(target=handle_client, args=(conn,)).start()

if __name__ == "__main__":
    start_daemon()