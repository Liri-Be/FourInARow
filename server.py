import json
import socket
import threading
import random
from time import sleep

IP = "127.0.0.1"
PORT = 10000
SOCKET_TIMEOUT = 6000
COLS = 7
ROWS = 6


def findPlaceToDrop(column, player, matrix):
    """
    Find the place to put the token to
    :param column: the column to drop in
    :param player: 1 or 2 - the player number
    :param matrix: The matrix of the game - values
    :return msg with the place in the board or msg that says the column is full:
    """
    msg = ""
    for i in range(ROWS):
        if matrix[i][column] == 0:
            matrix[i][column] = player
            msg = str(i + 1) + ',' + str(column + 1)
            break  # quit the loop
    if msg == "":
        msg = "Full column"
    return msg


def checkWin(matrix):
    """
    check if there is a win and if so, who won - check if there are 4 same symbols in row, column or diagonal
    :param matrix: The game board - matrix with values
    :return:
    """
    # check for win for 4 in row
    for i in range(ROWS):
        curr_player = matrix[i][0]
        count_tokens = 1
        for j in range(1, COLS):
            if curr_player == matrix[i][j] and curr_player != 0:  # found token that creates a row
                count_tokens += 1
                if count_tokens == 4:  # found 4 tokens in a row
                    msg = "Computer won!\n" if curr_player == 1 else "You won!\n"
                    return msg
            else:  # found different token that breaks the row
                count_tokens = 1
                curr_player = matrix[i][j]

    # check for win for 4 in column
    for i in range(COLS):
        curr_player = matrix[0][i]
        count_tokens = 1
        for j in range(1, ROWS):
            if curr_player == matrix[j][i] and curr_player != 0:  # found token that creates a column
                count_tokens += 1
                if count_tokens == 4:  # found 4 tokens in a column
                    msg = "Computer won!\n" if curr_player == 1 else "You won!\n"
                    return msg
            else:  # found different token that breaks the column
                count_tokens = 1
                curr_player = matrix[j][i]

    # check for win for 4 in diagonal
    for i in range(ROWS):
        curr_player = matrix[0][i]
        count_tokens = 1
        for j in range(COLS):
            for k in range(i + 1, i + 5):
                try:
                    if curr_player == matrix[i+k][j+k] and curr_player != 0:  # found token that creates a diagonal
                        count_tokens += 1
                        if count_tokens == 4:  # found 4 tokens in a diagonal
                            msg = "Computer won!\n" if curr_player == 1 else "You won!\n"
                            return msg
                    else:  # found different token that breaks the diagonal
                        count_tokens = 1
                        curr_player = matrix[j][i]
                except IndexError:
                    break

    return "No win"


def play_easy(client_socket, matrix):
    """
    Controls the game - easy level, chooses column for the server to place it's dice,
    and place the dice in the column from the client.
    :param client_socket: the client socket
    :param matrix: The matrix of the game - values
    :return None:
    """
    done = False
    while not done:
        # server turn
        client_socket.send("Computer's turn".encode())  # send it's the computer turn
        rand = random.randrange(COLS)
        msg = findPlaceToDrop(rand, 1, matrix)
        while "Full" in msg:  # the column is full
            rand = random.randrange(COLS)
            msg = findPlaceToDrop(rand, 1, matrix)
        sleep(0.3)

        client_socket.send(json.dumps(matrix).encode())  # let the client know where the token is
        msg = checkWin(matrix)
        sleep(0.3)
        if "won!" in msg:
            client_socket.send(msg.encode())
            break
        else:
            client_socket.send("Your turn".encode())

        # client turn
        try:
            wc = client_socket.recv(1024).decode()  # get user's column
        except socket.timeout:
            client_socket.close()
            print("client closed - timeout")
            return
        wc = int(wc) - 1
        msg = findPlaceToDrop(wc, 2, matrix)

        while "Full" in msg:  # the column is full
            client_socket.send("The column is full, choose a new one".encode())
            try:
                wc = client_socket.recv(1024).decode()
            except socket.timeout:
                client_socket.close()
                print("client closed - timeout")
                return
            wc = int(wc) - 1
            msg = findPlaceToDrop(wc, 2, matrix)

        client_socket.send(json.dumps(matrix).encode())  # let the client know where the token is
        msg = checkWin(matrix)
        if "won!" in msg:
            client_socket.send(msg.encode())
            done = True

    handle_client(client_socket)  # return to main "screen"


def play_hard(client_socket, matrix):
    """
    Controls the game - easy level, chooses column for the server to place it's dice,
    and place the dice in the column from the client.
    :param client_socket: the client socket
    :param matrix: The matrix of the game - values, game board
    :return None:
    """
    pass


def play_with_server(client_socket):
    """
    Control the part when the client chooses what level they want to play.
    :param client_socket: The client socket
    :return None:
    """
    matrix = [[0*x*y for x in range(COLS)] for y in range(ROWS)]  # game board
    msg = "Choose difficulty level:\n1. Easy\n2. Hard"
    client_socket.send(msg.encode("utf-8"))
    try:
        option = client_socket.recv(1024).decode("utf-8")
    except socket.timeout:
        # closing connection if the client didn't respond before timeout happened
        client_socket.close()
        print("client closed - timeout")
        return

    if '1' in option:  # easy
        play_easy(client_socket, matrix)
    if '2' in option:  # hard
        play_hard(client_socket, matrix)


def handle_client(client_socket):
    """
    Controls the start of the game - whether the client wants to play with the server or not
    :param client_socket: The client socket
    :return None:
    """
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

    if option is '1':  # play
        play_with_server(client_socket)
    if option is '2':  # quit
        client_socket.close()
        print("client left")


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # start the connection - tcp
    server_socket.bind((IP, PORT))  # connect to ip and port
    server_socket.listen(5)  # set amount of clients that can connect

    while True:
        client_socket, client_address = server_socket.accept()  # accept new client
        print('New connection received')
        client_socket.settimeout(SOCKET_TIMEOUT)  # set timeout to the client

        thread = threading.Thread(target=handle_client, args=(client_socket,))  # create new thread to the client
        thread.start()


if __name__ == '__main__':
    main()
