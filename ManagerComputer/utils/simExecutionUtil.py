import socket
import threading
import time

from utils.ManagerClass import ManagerServerData
from utils.utils import get_value_from_config_ini, receive_msgpack, send_msgpack


def bootup_computers():
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


def prepConnectedComp(conn, managerObj):
    while True:
        response = receive_msgpack(conn)
        if response and isinstance(response, dict) and response.get("stage") == "prep":
            compName = response["comp"]
            prepMsg = getCompPrepMsg(compName, managerObj)
            send_msgpack(conn, prepMsg)
            if prepMsg:
                print(prepMsg)
            return compName


def handle_computer(conn, addr):
    compName = prepConnectedComp(conn)
    compDetails = {"compName": compName, "socket": conn, "addr": addr}

    # Send update message to the main thread with the computer name and socket

    while True:
        try:
            msg = {"data": ["1", "2", "3"]}
            response = receive_msgpack(conn)
            send_msgpack(conn, msg)
            if response is not None:
                print(response)
        except Exception as e:
            print(f"Error with connection from {addr}: {e}")
            break
    conn.close()


def getManagerIP_and_PORT():
    host = get_value_from_config_ini("GENERAL", "manager_comp_ip")
    port = get_value_from_config_ini("GENERAL", "manager_PORT", "int")

    return host, port


def connectToComponents(managerObj):
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


def handle_simulation_execution(wsCommToSimThreadQ, simThreadToWsCommQ):
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


def waitForStartCommand(wsCommToSimThreadQ):
    if wsCommToSimThreadQ.empty():
        return None, None, None

    msg = wsCommToSimThreadQ.get()

    if not isinstance(msg, dict) or msg.get("stage") != "start":
        return None, None, None

    simulationRunning = True
    managerObj = ManagerServerData(startMsg=msg)
    computers = connectToComponents(managerObj)

    return simulationRunning, managerObj, computers
