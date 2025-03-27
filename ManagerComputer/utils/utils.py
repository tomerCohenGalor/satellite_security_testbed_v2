import struct
import msgpack
import yaml
import socket
import configparser

from pathlib import Path


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


def bootup_computers():
    daemonServersParameters = getDaemonServersParameters()
    manager_ip = get_value_from_config_ini('GENERAL' ,'manager_comp_ip')

    for daemonServerParameters in daemonServersParameters:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as daemonSocket:
                daemonSocket.settimeout(1)
                daemonSocket.connect((daemonServerParameters['ip'], daemonServerParameters['port']))
                send_msgpack(daemonSocket, ["main", manager_ip])
        except (ConnectionResetError, ConnectionAbortedError, TimeoutError) as e:
            print("couldn't connect to ", daemonServerParameters['computerName'])


def get_value_from_config_ini(sectionIdentifier: str, varIdentifier: str, varType:str='string') -> any:
    configFilePath = Path(__file__).parent.parent / 'config' / 'manager_config.ini'
    config=configparser.ConfigParser()
    config.read(configFilePath)

    if varType == 'int':
        return config.getint(sectionIdentifier, varIdentifier)
    if varType == 'string':
        return config.get(sectionIdentifier, varIdentifier)
    if varType == 'float':
        return config.getfloat(sectionIdentifier, varIdentifier)
    if varType == 'boolean':
        return config.getboolean(sectionIdentifier, varIdentifier)


def getDaemonServersParameters() -> list[dict[str, any]]:
    return [
        {
            'computerName': 'orbital',
            'ip': get_value_from_config_ini('GENERAL', 'dataConv_comp_IP'),
            'port': get_value_from_config_ini('GENERAL', 'daemon_server_PORT_ENV', varType='int')
        }, 
    ]
    
def getCompPrepMsg(compName):
    if compName == 'orbital':
        return {
            "stage": "prep",
            "type": "SEND",
            "data": {
                "tle": [
                    "PROGRESS-MS 26",
                    "1 58961U 24029A   24213.90256772  .00036721  00000+0  66014-3 0  9994",
                    "2 58961  51.6377  93.7862 0005973 147.7965 320.0621 15.49475947 25767"
                ],
                "time": [2024, 3, 23, 10, 33, 20.0],
                "min": 1369.7478539121023,
                "max": 1369.8887229789696
            }
        }

def prepConnectedComp(conn):
    while True:
        response = receive_msgpack(conn)
        if response and isinstance(response, dict) and response.get('stage') == 'prep':
            prepMsg = getCompPrepMsg(response['comp'])
            send_msgpack(conn, prepMsg)
            break