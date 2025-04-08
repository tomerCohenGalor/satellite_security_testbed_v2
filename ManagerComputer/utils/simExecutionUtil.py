import queue
import socket
import time

from utils.ManagerClass import ManagerServerData
from utils.utils import get_value_from_config_ini, receive_msgpack, send_msgpack


def bootup_computers():
    """
    Initiates the boot-up process for the three components computers(Operational, enviroment and orbital)
    by sending a 'main' command along with
    the manager computer's IP address to each daemon server.

    This function performs the following steps:
    1. Retrieves the list of daemon server parameters (IP, port, computer name, etc.).
    2. Retrieves the manager computer's IP address from the configuration file.
    3. Iterates over each daemon server and attempts to connect via a TCP socket, activation of the daemon server runs the component script.
    4. If the connection is successful, sends a MsgPack-encoded message to the server.
    5. If the connection fails due to a network error, prints an error message with the server name.

    Exceptions handled:
        - ConnectionResetError
        - ConnectionAbortedError
        - TimeoutError
    """
    daemonServersParameters = getDaemonServersParameters()
    manager_ip = get_value_from_config_ini("GENERAL", "manager_comp_ip")

    for daemonServerParameters in daemonServersParameters:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as daemonSocket:
                daemonSocket.settimeout(1)
                daemonSocket.connect(
                    (daemonServerParameters["ip"], daemonServerParameters["port"])
                )
                send_msgpack(daemonSocket, ["main", manager_ip])
        except (ConnectionResetError, ConnectionAbortedError, TimeoutError) as e:
            print("couldn't connect to ", daemonServerParameters["computerName"])


def getDaemonServersParameters() -> list[dict[str, any]]:
    """
    Retrieves the configuration parameters for all daemon servers involved in the system.

    Returns:
        list[dict[str, any]]: A list of dictionaries, each containing:
            - "computerName" (str): A label identifying the computer (e.g., 'orbital', 'operational', 'cyber').
            - "ip" (str): The IP address of the corresponding daemon server, read from the configuration file.
            - "port" (int): The port number used to communicate with the daemon server, also read from the config.

    Notes:
        - This function uses `get_value_from_config_ini` to fetch IP and port values from a config file.
        - The expected section in the config file is 'GENERAL', with specific keys for each computer's IP and port.
    """
    return [
        {
            "computerName": "orbital",
            "ip": get_value_from_config_ini("GENERAL", "dataConv_comp_IP"),
            "port": get_value_from_config_ini(
                "GENERAL", "daemon_server_PORT_ENV", varType="int"
            ),
        },
        {
            "computerName": "operational",
            "ip": get_value_from_config_ini("GENERAL", "operational_comp_IP"),
            "port": get_value_from_config_ini(
                "GENERAL", "daemon_server_PORT_OP", varType="int"
            ),
        },
        {
            "computerName": "cyber",
            "ip": get_value_from_config_ini("GENERAL", "cyber_comp_IP"),
            "port": get_value_from_config_ini(
                "GENERAL", "daemon_server_PORT_CYBER", varType="int"
            ),
        },
    ]


def getCompPrepMsg(compName: str, managerObj: ManagerServerData):
    """
    Constructs and returns a preparation message for a specific computer based on its role.

    Args:
        compName (str): The name of the target computer. Expected values are:
                        - "orbital"
                        - "operational"
                        - "cyber"
        managerObj (ManagerServerData): An object containing all necessary data (TLE, time, probabilities, etc.)
                                        used to populate the message payload.

    Returns:
        dict: A dictionary representing the message to send, with the following structure:
              {
                  "stage": "prep",
                  "type": "SEND",
                  "data": {...}  # Varies depending on the computer
              }

              - For "orbital": includes 'tle', 'time', 'min', 'max'
              - For "operational": includes 'time', 'tle', 'night_probability'
              - For "cyber": includes 'time', 'tle', 'attacks'
    """
    if compName == "orbital":
        return {
            "stage": "prep",
            "type": "SEND",
            "data": {
                "tle": managerObj.tle,
                "time": managerObj.time,
                "min": managerObj.min,
                "max": managerObj.max,
            },
        }
    if compName == "operational":
        return {
            "stage": "prep",
            "type": "SEND",
            "data": {
                "time": managerObj.time,
                "tle": managerObj.tle,
                "night_probability": managerObj.night_probability,
            },
        }
    if compName == "cyber":
        return {
            "stage": "prep",
            "type": "SEND",
            "data": {
                "time": managerObj.time,
                "tle": managerObj.tle,
                "attacks": managerObj.attacks,
            },
        }


def prepConnectedComp(conn: socket, managerObj: ManagerServerData):
    """
    Handles the preparation phase for a connected component by responding to a 'prep' request.

    Listens on the provided socket connection for a MsgPack-encoded message from the client.
    If the message indicates that the component is in the 'prep' stage, the function constructs
    and sends back a preparation message using the provided manager object.

    Args:
        conn (socket): The socket object representing the connection to the component.
        managerObj (ManagerServerData): An object containing data needed to construct the preparation message
                                        (e.g., TLE, time, attacks, etc).

    Returns:
        str: The name of the component (e.g., "orbital", "operational", "cyber") once preparation is complete.

    Behavior:
        - Waits for a valid dictionary message with "stage": "prep".
        - Extracts the component name from the message.
        - Sends a corresponding preparation message built using `getCompPrepMsg()`.
        - Returns the component name to indicate which component was prepared.
    """
    while True:
        response = receive_msgpack(conn)
        if response and isinstance(response, dict) and response.get("stage") == "prep":
            compName = response["comp"]
            prepMsg = getCompPrepMsg(compName, managerObj)
            send_msgpack(conn, prepMsg)
            return compName


def getManagerIP_and_PORT() -> tuple[str, int]:
    """
    Retrieves the IP address and port number of the manager computer from the configuration file.

    Returns:
        tuple[str, int]: A tuple containing:
            - host (str): The manager computer's IP address.
            - port (int): The port number used for manager communication.

    Notes:
        - Values are read from the "GENERAL" section of the config file using `get_value_from_config_ini`.
        - The 'manager_PORT' value is explicitly cast to an integer.
    """
    host = get_value_from_config_ini("GENERAL", "manager_comp_ip")
    port = get_value_from_config_ini("GENERAL", "manager_PORT", "int")

    return host, port


def connectToComponents(managerObj: ManagerServerData):
    """
    Boots up all component computers, listens for their connections, and prepares them for operation.

    This function performs the following:
    1. Sends boot-up messages to all daemon servers.
    2. Starts a server socket using the manager's IP and port (from the config).
    3. Accepts incoming connections from component computers.
    4. For each connection, performs a preparation handshake using `prepConnectedComp`.
    5. Stores and returns information about each connected and prepared computer.

    Args:
        managerObj (ManagerServerData): An object containing all the relevant data to be sent to components
                                        during their preparation phase (e.g., TLE, time, min, max, etc.).

    Returns:
        list[dict]: A list of dictionaries, each representing a connected computer with:
            - "compName" (str): The name of the component (e.g., "orbital", "operational", "cyber").
            - "socket" (socket): The socket object representing the connection.
            - "addr" (tuple): The (IP, port) address of the connected client.

    Notes:
        - Expects exactly 3 computers to connect and complete preparation.
        - Assumes `bootup_computers` will successfully initiate each component.
        - This function blocks until all components are connected and ready.
    """
    computers = []
    numberOfComputers = 3

    bootup_computers()

    host, port = getManagerIP_and_PORT()

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen()

    while len(computers) < numberOfComputers:
        conn, addr = server_socket.accept()
        compName = prepConnectedComp(conn, managerObj)
        computers.append({"compName": compName, "socket": conn, "addr": addr})

    return computers


def handle_simulation_execution(wsCommToSimThreadQ: queue, simThreadToWsCommQ: queue):
    simulationRunning = False

    while True:
        simulationRunning, managerObj, computers = waitForStartCommand(
            wsCommToSimThreadQ
        )

        while simulationRunning:

            time.sleep(2)

            # DOCUMENTATION
            # process_inputs()
            # update_simulation_state()
            # send_outputs_if_needed()
            # sleep_or_wait()  # Maintain simulation timing


def waitForStartCommand(wsCommToSimThreadQ: queue):
    if wsCommToSimThreadQ.empty():
        return None, None, None

    msg = wsCommToSimThreadQ.get()

    if not isinstance(msg, dict) or msg.get("stage") != "start":
        return None, None, None

    simulationRunning = True
    managerObj = ManagerServerData(startMsg=msg)
    computers = connectToComponents(managerObj)

    return simulationRunning, managerObj, computers
