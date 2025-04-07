import struct
import msgpack
import yaml
import configparser

from pathlib import Path


def receive_msgpack(comp_socket) -> dict:
    """
    Receives a message from a socket and unpacks it using msgpack.

    :param comp_socket: The socket object from which to receive the message.
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
    Serializes and sends a message over a socket using msgpack.

    :param comp_socket: The socket object through which to send the message.
    :param msg: The message (dictionary) to be sent.
    """
    packed_data = msgpack.packb(msg, use_bin_type=True)
    length = struct.pack("I", len(packed_data))
    comp_socket.sendall(length + packed_data)


def serialize_yaml(path: str):
    """
    Reads a YAML file and returns its contents as a dictionary.

    :param path: The file path to the YAML file.
    :return: A dictionary representing the YAML data.
    """
    with open(path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    return data


def get_value_from_config_ini(
    sectionIdentifier: str, varIdentifier: str, varType: str = "string"
) -> any:
    """
    Retrieves a value from a configuration INI file based on the provided section and variable identifiers.

    :param sectionIdentifier: The section name in the INI file.
    :param varIdentifier: The variable name within the section.
    :param varType: The expected data type ('int', 'string', 'float', or 'boolean'). Defaults to 'string'.
    :return: The value from the configuration file in the specified type.
    """
    configFilePath = Path(__file__).parent.parent / "config" / "sim_config.ini"
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
