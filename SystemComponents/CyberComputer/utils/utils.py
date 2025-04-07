import struct
import msgpack
import yaml
import datetime
import configparser

from pathlib import Path


def receive_msgpack(comp_socket) -> dict:
    """
    Receives and decodes a MessagePack-formatted message from a socket.

    Parameters:
    comp_socket (socket.socket): The socket from which to receive data.

    Returns:
    dict: The unpacked MessagePack data as a dictionary. Returns an empty dictionary if no data is received.

    Behavior:
    - Reads the first 4 bytes to determine the length of the incoming message.
    - Continues receiving data in chunks until the full message is received.
    - Unpacks the received data using MessagePack and returns it as a dictionary.
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
    Encodes and sends a MessagePack-formatted message over a socket.

    Parameters:
    comp_socket (socket.socket): The socket through which to send data.
    msg (dict): The dictionary to be serialized and sent.

    Behavior:
    - Serializes the message using MessagePack.
    - Sends the length of the packed message as a 4-byte header.
    - Sends the serialized message over the socket.
    """
    packed_data = msgpack.packb(msg, use_bin_type=True)
    length = struct.pack("I", len(packed_data))
    comp_socket.sendall(length + packed_data)


def serialize_yaml(path: str):
    """
    Reads and parses a YAML file.

    Parameters:
    path (str): The file path to the YAML file.

    Returns:
    dict: The parsed data from the YAML file.

    Behavior:
    - Opens the specified YAML file.
    - Parses its contents using `yaml.safe_load()`.
    - Returns the data as a dictionary.
    """
    with open(path, "r") as yaml_file:
        data = yaml.safe_load(yaml_file)

    return data


def to_unix_time(time_fmt):
    """
    Converts a given time format to a Unix timestamp.

    Parameters:
    time_fmt (tuple): A tuple containing (year, month, day, hour, minute, float_seconds).

    Returns:
    float: The Unix timestamp representation of the given time.

    Behavior:
    - Constructs a `datetime` object from the provided time components.
    - Adjusts for fractional seconds.
    - Converts the datetime object to a UTC timestamp.
    """
    time_fmt = tuple(time_fmt)
    year, month, day, hour, minute, float_seconds = time_fmt
    dt = datetime.datetime(year, month, day, hour, minute, int(float_seconds))
    dt = dt + datetime.timedelta(seconds=float_seconds - int(float_seconds))
    return dt.replace(tzinfo=datetime.timezone.utc).timestamp()


def get_value_from_config_ini(
    sectionIdentifier: str, varIdentifier: str, varType: str = "string"
) -> any:
    """
    Retrieves a configuration value from a `cyber_config.ini` file.

    Parameters:
    sectionIdentifier (str): The section name in the INI file.
    varIdentifier (str): The variable name within the section.
    varType (str, optional): The expected type of the value. Defaults to 'string'.
                             Valid options: 'string', 'int', 'float', 'boolean'.

    Returns:
    any: The retrieved value, cast to the specified type.

    Behavior:
    - Reads the `cyber_config.ini` file located in the `config` directory.
    - Extracts the requested value and converts it to the specified type.
    - Supports integer, float, boolean, and string values.
    """
    configFilePath = Path(__file__).parent.parent / "config" / "cyber_config.ini"
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
