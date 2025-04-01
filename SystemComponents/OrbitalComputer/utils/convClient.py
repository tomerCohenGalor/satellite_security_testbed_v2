import socket

from utils.utils import receive_msgpack, send_msgpack


class Client:
    def __init__(self, host, port, computer_name):
        """
        Initializes the Client instance.
        
        :param host: The IP address of the server.
        :param port: The port number to connect to.
        :param computer_name: The name of the client computer.
        """
        self.manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager_addr = (host, port)
        self.computer_name = computer_name

    def execute(self, options=None):  # options - the entire data collected by the machine as a dictionary
        """
        Sends execution data to the manager server that could contain parameters and retrieves a response.
        
        :param options: A dictionary containing the data collected by the machine (default is an empty dictionary).
        :return: The response data received from the server.
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
        Sends a prep request to the server and retrieves relevant data.
        
        :return: A tuple containing TLE data, time data, and a tuple of min/max values.
        """
        prep_msg: dict = {
            "stage": "prep",
            "type": "REQUEST",
            "comp": self.computer_name
        }
        send_msgpack(self.manager_socket, prep_msg)

        request_msg = receive_msgpack(self.manager_socket)
        request_msg_data = request_msg.get('data')

        return request_msg_data.get('tle'), request_msg_data.get('time'), (request_msg_data.get('min'), request_msg_data.get('max'))

    def run(self):
        """
        Establishes a connection to the server.
        """
        self.manager_socket.connect(self.manager_addr)

