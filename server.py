import socket
import threading
from random import random

IP = "127.0.0.1"
PORT = 10000
SOCKET_TIMEOUT = 30
w = 7
h = 6


class PlaceInMatrix:
    """
    Class to handle the game - to know what happens in every place on the board
    """
    def __init__(self):
        self.checked = False
        self.value = None


Matrix = [[PlaceInMatrix() for x in range(w)] for y in range(h)]


def play_easy(client_socket):
    done = False
    while not done:
        rand = random(range(w))
        for i in range(h):
            if Matrix[i][rand] is 0:
                Matrix[i][rand] = 1
                msg = str(i) + ',' + str(rand)
                client_socket.send(msg.encode("utf-8"))
                break  # quit the loop
        try:
            [hc, wc] = client_socket.recv().decode().split(",")
            Matrix[hc][wc] = 2
        except():
            client_socket.close()
            print("client closed - timeout")


def play_hard(client_socket):
    pass


def play_with_server(client_socket):
    msg = "Choose difficulty level:\n1. Easy\n2. Hard"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv().decode("utf-8")
    except():
        # closing connection if the client didn't respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    if '1' in option:
        play_easy(client_socket)
    if '2' in option:
        play_hard(client_socket)


def handle_client(client_socket):
    # handling clients
    msg = "choose option:\n1. Play with server \n2. Quit"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv(1024).decode("utf-8")
    except():
        # closing connection if the client didn't respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    if option is '1':
        play_with_server(client_socket)
    if option is '2':
        client_socket.close()
        print("client left")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)

        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


if __name__ == '__main__':
    main()
