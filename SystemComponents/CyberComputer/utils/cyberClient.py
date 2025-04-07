import socket

from utils.utils import receive_msgpack, send_msgpack


class Client:
    """
    A client that connects to a manager server, sends requests, and receives responses.

    Attributes:
    - manager_socket (socket.socket): The TCP socket used for communication.
    - manager_addr (tuple): The (host, port) tuple of the manager server.
    - computer_name (str): The name of the computer sending requests.

    Methods:
    - execute(options=None): Sends an execution request with optional parameters.
    - prep(): Sends a preparation request and retrieves attack data and the current minute.
    - run(): Establishes a connection with the manager server.
    """

    def __init__(self, host, port, computer_name):
        """
        Initializes the Client with a specified manager server address.

        Parameters:
        - host (str): The IP address or hostname of the manager server.
        - port (int): The port number of the manager server.
        - computer_name (str): The name of the client computer.
        """
        self.selected_options = None
        self.manager_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.manager_addr = (host, port)
        print(self.manager_addr)
        self.computer_name = computer_name

    def execute(self, options=None):
        """
        Sends an execution request to the manager server.

        Parameters:
        - options (dict, optional): Additional execution options to include in the request. Defaults to an empty dictionary.

        Returns:
        - dict: The response message received from the manager server.

        Behavior:
        - Waits for and returns the response from the manager.
        """
        if options is None:
            options = {}
        share_msg: dict = {
            "stage": "execution",
            "type": "SHARE",
            "data": {"options": {}},
        }
        share_msg["data"]["options"].update(options)

        send_msgpack(self.manager_socket, share_msg)
        exe_data = receive_msgpack(self.manager_socket)

        return exe_data

    def prep(self):
        """
        Sends a preparation request to the manager server and retrieves attack information.

        Returns:
        - tuple: (attacks, current_minute), where:
          - attacks (list): A list of attacks received from the server.
          - current_minute (int): The current time in minutes according to the manager.

        Behavior:
        - Sends a "REQUEST" message with the computer name to request preparation data.
        - Receives and extracts attack details and the current minute from the response.
        """
        prep_msg: dict = {
            "stage": "prep",
            "type": "REQUEST",
            "comp": self.computer_name,
        }
        send_msgpack(self.manager_socket, prep_msg)

        request_msg = receive_msgpack(self.manager_socket)
        request_msg_data = request_msg.get("data")

        return (request_msg_data.get("attacks"), request_msg_data.get("current_minute"))

    def run(self):
        """
        Establishes a connection to the manager server.

        Behavior:
        - Attempts to connect to the server using the specified address.
        - Prints a message indicating the connection status.
        """
        print(f"connecting to {self.manager_addr}")
        self.manager_socket.connect(self.manager_addr)
