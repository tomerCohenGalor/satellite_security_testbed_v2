import threading
import socket


from utils.utils import receive_msgpack, send_msgpack, getDaemonDetails, bootup_computers





def handle_client(conn, addr):
    print(f"New connection from {addr}")
    #prep
    prep_msg={
    "stage": "prep",
    "type": "SEND",
    "data": {
        "tle": [
            "PROGRESS-MS 26",
            "1 58961U 24029A   24213.90256772  .00036721  00000+0  66014-3 0  9994",
            "2 58961  51.6377  93.7862 0005973 147.7965 320.0621 15.49475947 25767"
        ],
        "time": [
            2024,
            3,
            23,
            10,
            33,
            20.0
        ],
        "min": 1369.7478539121023,
        "max": 1369.8887229789696
    }
}


    # Wait for the prep message from the computer
    while True:
        response = receive_msgpack(conn)
        if response and isinstance(response, dict) and response.get('stage') == 'prep':
            send_msgpack(conn, prep_msg)
            break


    while True:
        try:
            # message = conn.recv(1024).decode()
            # if message:
            #     print(f"Message from {addr}: {message}")
            #     conn.send(message.encode())
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

    host = '127.0.0.1'
    port = 13020

    server_socket = socket.socket()
    server_socket.bind((host, port))
    server_socket.listen()

    while True:
        conn, addr = server_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"Active connections: {threading.active_count() - 1}")




if __name__ == '__main__':
    try:
        startManagerServer()
    except Exception as e:  # Catches any other unexpected errors
        print(f"Unexpected error occurred: {e}")