import socket

from utils.utils import receive_msgpack, send_msgpack


class Client:
    """
    A client class to manage communication with the manager server via sockets.
    """
    def __init__(self, host, port, computer_name):
        """
        Initializes the Client instance that will later be used to communicate with the manager computer.
        
        :param host: The IP address of the manager server.
        :param port: The port number of the manager server.
        :param computer_name: The name of the computer connecting to the manager.
        """
        self.manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager_addr = (host, port)
        self.computer_name = computer_name

    def execute(self, options={}):  # options - the entire data collected by the machine as a dictionary
        """
        Sends execution request to the manager and retrieves the response.
        
        :param options: A dictionary containing collected data from the machine (default: empty dictionary).
        :return: The response data received from the manager.
        """
        if options is None:
            options = {}
        share_msg: dict = {
            "stage": "execution",
            "type": "SHARE",
            "data": {
                "options": {}
            }
        }
        share_msg["data"]["options"].update(options)

        send_msgpack(self.manager_socket, share_msg)
        exe_data = receive_msgpack(self.manager_socket)
        
        return exe_data

    def prep(self):
        """
        Sends a prep request to the manager and retrieves required initialization data.
        
        :return: A tuple containing TLE data, time data, and night probability from the response.
        """
        prep_msg: dict = {
            "stage": "prep",
            "type": "REQUEST",
            "comp": self.computer_name
        }
        send_msgpack(self.manager_socket, prep_msg)

        request_msg = receive_msgpack(self.manager_socket)
        request_msg_data = request_msg.get('data')

        print(request_msg_data)
    
        return request_msg_data.get('tle'), request_msg_data.get('time'), request_msg_data.get('night_probability')

    def run(self):
        """
        Establishes a connection to the manager server.
        """
        self.manager_socket.connect(self.manager_addr)

