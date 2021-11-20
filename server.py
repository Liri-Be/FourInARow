import socket
import threading
import random

IP = "127.0.0.1"
PORT = 10000
SOCKET_TIMEOUT = 6000
COLS = 7
ROWS = 6


class PlaceInMatrix:
    """
    Class to handle the game - to know what happens in every place on the board
    """
    def __init__(self):
        self.checked = False
        self.value = None


Matrix = [[PlaceInMatrix() for x in range(COLS)] for y in range(ROWS)]


def findPlaceToDrop(column, player):
    """
    Find the place to put the token to
    :param column: the column to drop in
    :param player: 1 or 2 - the player number
    :return msg with the place in the board or msg that says the column is full:
    """
    msg = ""
    for i in range(ROWS):
        if not Matrix[i][column].checked:
            Matrix[i][column].checked = True
            Matrix[i][column].value = player
            msg = str(i + 1) + ',' + str(column + 1)
            break  # quit the loop
    if msg == "":
        msg = "Full column"
    return msg


def play_easy(client_socket):
    done = False
    while not done:
        # server turn
        rand = random.randrange(COLS)
        msg = findPlaceToDrop(rand, 1)
        while "Full" in msg:
            rand = random.randrange(COLS)
            msg = findPlaceToDrop(rand, 1)

        client_socket.send(msg.encode("utf-8"))  # let the client know where the token is
        # call win function

        # client turn
        try:
            wc = client_socket.recv(1024).decode()
        except socket.timeout:
            client_socket.close()
            print("client closed - timeout")
            return

        wc = int(wc) - 1
        msg = findPlaceToDrop(wc, 2)
        while "Full" in msg:
            msg = findPlaceToDrop(wc, 2)


def play_hard(client_socket):
    pass


def play_with_server(client_socket):
    msg = "Choose difficulty level:\n1. Easy\n2. Hard"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv(1024).decode("utf-8")
    except socket.timeout:
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
    except socket.timeout:
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
