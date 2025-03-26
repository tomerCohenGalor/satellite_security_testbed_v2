import struct
import msgpack
import yaml
import socket


def receive_msgpack(comp_socket) -> dict:
    length_bytes = comp_socket.recv(4)
    if not length_bytes:
        return {}
    length = struct.unpack('I', length_bytes)[0]

    packed_data = b""
    while len(packed_data) < length:
        chunk = comp_socket.recv(1024)
        if not chunk:
            break
        packed_data += chunk

    if packed_data:
        msg = msgpack.unpackb(packed_data, raw=False)
        return msg
    return {}


def send_msgpack(comp_socket, msg):
    packed_data = msgpack.packb(msg, use_bin_type=True)
    length = struct.pack('I', len(packed_data))
    comp_socket.sendall(length + packed_data)


def serialize_yaml(path: str):
    with open(path, 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)

    return data

def getDaemonDetails():
    print()

def bootup_computers(daemonServerParameters):
    daemonServerParameters = [
        {
            'computerName': 'orbital',
            'ip': '127.0.0.1',
            'port': 13022
        }
    ]
    
    orbitalDaemonIP = "127.0.0.1"
    orbitalDaemonPORT = 13022
    manager_ip = '127.0.0.1'

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as daemonSocket:
            daemonSocket.settimeout(1)
            daemonSocket.connect((orbitalDaemonIP, orbitalDaemonPORT))
            to_start = ["main", manager_ip]
            send_msgpack(daemonSocket, to_start)
    except (ConnectionResetError, ConnectionAbortedError, TimeoutError) as e:
        print("couldn't connect ")
    