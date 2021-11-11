import socket
import threading
from random import random

IP = "127.0.0.1"
PORT = 10000
SOCKET_TIMEOUT = 30
w = 7
h = 6
Matrix = [[0 for x in range(w)] for y in range(h)]


def play_easy(client_socket):
    end = False
    while not end:
        rand = random(0, range(w))
        for i in range(h):
            if Matrix[i][rand] is 0:
                Matrix[i][rand] = 1
                msg = str(i) + ',' + str(rand)
                client_socket.send(msg.encode("utf-8"))
                i = h  # quit the loop
        try:
            [Hc, Wc] = client_socket.recv().decode().split(",")
            Matrix[Hc][Wc] = 2
        except():
               client_socket.close()
               print("client closed - timeout")


def play_hard(client_socket):
    pass


def play_with_server(client_socket):
    msg = "choose difficulty level:\n1. easy\n2. hard"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv().decode("utf-8")
    except():
        # closing connection if the client didnt respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    if '1' in option:
        play_easy(client_socket)
    if '2' in option:
        play_hard(client_socket)



def handle_client(client_socket):
    # handling clients
    msg = "choose option:\n1. quit \n2. play with server"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv().decode("utf-8")
    except():
        # closing connection if the client didnt respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    if option is '1':
        client_socket.close()
        print("client left")
    if option is '2':
        play_with_server(client_socket)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)

        thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        thread.start()


if __name__ == '__main__':
    main()
