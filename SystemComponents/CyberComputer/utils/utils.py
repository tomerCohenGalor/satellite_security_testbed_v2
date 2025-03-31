import struct
import msgpack
import yaml
import datetime
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

def to_unix_time(time_fmt):
    time_fmt = tuple(time_fmt)
    year, month, day, hour, minute, float_seconds = time_fmt
    dt = datetime.datetime(year, month, day, hour, minute, int(float_seconds))
    dt = dt + datetime.timedelta(seconds=float_seconds - int(float_seconds))
    return dt.replace(tzinfo=datetime.timezone.utc).timestamp()


def get_value_from_config_ini(sectionIdentifier: str, varIdentifier: str, varType:str='string') -> any:
    configFilePath = Path(__file__).parent.parent / 'config' / 'cyber_config.ini'
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
