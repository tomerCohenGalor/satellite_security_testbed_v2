import struct
import msgpack
import yaml
import configparser

from pathlib import Path


def receive_msgpack(comp_socket) -> dict:
    """
    Receives and unpacks a MessagePack-encoded message from a socket.

    :param comp_socket: The socket from which to receive the message.
    :return: A dictionary containing the unpacked message data.
    """
    length_bytes = comp_socket.recv(4)
    if not length_bytes:
        return {}
    length = struct.unpack("I", length_bytes)[0]

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
    """
    Packs and sends a dictionary as a MessagePack-encoded message over a socket.

    :param comp_socket: The socket to send the message through.
    :param msg: The dictionary to be packed and sent.
    """
    packed_data = msgpack.packb(msg, use_bin_type=True)
    length = struct.pack("I", len(packed_data))
    comp_socket.sendall(length + packed_data)


def serialize_yaml(path: str):
    """
    Loads and returns data from a YAML file.

    :param path: The path to the YAML file.
    :return: The parsed YAML data.
    """
    with open(path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    return data


def get_value_from_config_ini(
    sectionIdentifier: str, varIdentifier: str, varType: str = "string"
) -> any:
    """
    Retrieves a value from a configuration INI file.

    :param sectionIdentifier: The section in the INI file.
    :param varIdentifier: The variable name within the section.
    :param varType: The expected type of the variable ('string', 'int', 'float', 'boolean'). Defaults to 'string'.
    :return: The retrieved value, cast to the appropriate type.
    """
    configFilePath = Path(__file__).parent.parent / "config" / "dataConv_config.ini"
    config = configparser.ConfigParser()
    config.read(configFilePath)

    if varType == "int":
        return config.getint(sectionIdentifier, varIdentifier)
    if varType == "string":
        return config.get(sectionIdentifier, varIdentifier)
    if varType == "float":
        return config.getfloat(sectionIdentifier, varIdentifier)
    if varType == "boolean":
        return config.getboolean(sectionIdentifier, varIdentifier)
