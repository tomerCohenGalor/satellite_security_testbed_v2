import threading
import socket


from utils.utils import (
    receive_msgpack, 
    send_msgpack, 
    bootup_computers,
    get_value_from_config_ini,
    prepConnectedComp
)


def handle_computer(conn, addr):
    prepConnectedComp(conn)

    while True:
        try:
            msg = {
                "data": ['1' , '2', '3']
            }
            response = receive_msgpack(conn)
            send_msgpack(conn, msg)
            if response:
                print(response)
        except Exception as e:
            print(f"Error with connection from {addr}: {e}")
            break
    conn.close()

def startManagerServer():
    bootup_computers()

    host = get_value_from_config_ini('GENERAL', 'manager_comp_ip')
    port = get_value_from_config_ini('GENERAL', 'manager_PORT', 'int')
    
    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_computer, args=(conn, addr))
        thread.start()
        print(f"Active connections: {threading.active_count() - 1}")




if __name__ == '__main__':
    startManagerServer()