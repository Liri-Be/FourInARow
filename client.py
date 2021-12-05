import json
import socket
from time import sleep

IP = "127.0.0.1"
PORT = 10000


def playTheGame(c_soc, rounds):
    """
    Plays the game until got to the desired amount of wins
    :param c_soc: the socket to connect to server
    :param rounds: number of desired wins
    :return None:
    """
    cnt = 0
    while cnt != rounds:
        if playOneTurn(c_soc):
            cnt += 1
        try:
            print(c_soc.recv(1024).decode())  # stats from server - round
        except socket.timeout:
            c_soc.close()
            return

    try:
        print(c_soc.recv(1024).decode())  # stats from server - game
    except socket.timeout:
        c_soc.close()
        return
    sleep(1)
    chooseTheGame(c_soc)  # returns to main "screen"


def playOneTurn(c_soc):
    """
    Handles the process of the game, one turn, from the client side
    :param c_soc: The socket for connection to server
    :return True if the user have won, False otherwise:
    """
    finish = False
    while not finish:
        try:
            data_from_server = c_soc.recv(1024).decode()
            if "won!" in data_from_server:  # Win
                print(data_from_server)
                sleep(0.3)
                return True if "You" in data_from_server else False  # To know if the user won

            elif "Your" in data_from_server or "full" in data_from_server:  # signal for user's turn or column is full
                print(data_from_server)
                # choose a place to drop
                column = input("Choose column to drop in (1-7): ")
                while not column.isdigit() or (int(column) > 7 or int(column) < 1):
                    column = input("Choose column to drop in (1-7): ")
                c_soc.send(column.encode())

            elif "Computer's" in data_from_server:  # signal for computer's game
                print(data_from_server)

            else:
                matrix = json.loads(data_from_server)  # matrix
                for i in range(5, -1, -1):
                    for j in range(7):
                        if j == 6:
                            print(str(matrix[i][j]))
                        else:
                            print(str(matrix[i][j]), end=", ")
                print()

        except socket.timeout:
            print("Timed out")
            c_soc.close()
            return


def chooseRounds(c_soc):
    """
    Controls the part of choosing the desired amount of wins to win a game
    :param c_soc: The socket that connects to the server
    :return None:
    """
    try:
        print(c_soc.recv(1024).decode())  # choose the amount of wins
    except socket.timeout:
        c_soc.close()
        return

    done = False
    data_from_server = ""
    first = True
    while not done:
        msg = "" if first else "Choose amount: "  # at first don't ask for number, because server asks
        amount = input(msg)  # get number
        c_soc.send(amount.encode())  # send to server
        first = False  # if failed, start ask for number
        try:
            data_from_server = c_soc.recv(1024).decode()  # choose to start the game or not
        except socket.timeout:
            c_soc.close()
            return
        if "Not" in data_from_server:
            print(data_from_server)
            if "failed" in data_from_server:
                seconds = int(data_from_server.split()[8])
                sleep(seconds / 5)
        else:
            done = True

    # play the game until the user wins the selected amount
    try:
        print(c_soc.recv(1024).decode())  # welcome
    except socket.timeout:
        c_soc.close()
        return
    playTheGame(c_soc, int(data_from_server.split(", ")[1]))


def chooseTheGame(c_soc):
    """
    Handles the process of choosing whether the users want to play,
    and if so choosing the level of the game, from the client side
    :param c_soc: The socket for connection to server
    :return None:
    """
    try:
        print(c_soc.recv(1024).decode())  # choose to start the game or not
    except socket.timeout:
        c_soc.close()
        return

    option = input("Choose number (1 or 2): ")  # get data from user
    while not option.isdigit() or (int(option) > 2 or int(option) < 1):
        option = input("Choose number (1 or 2): ")
    c_soc.send(option.encode())  # send to server
    if option == '2':
        c_soc.close()
        return

    try:
        print(c_soc.recv(1024).decode())  # choose the level
    except socket.timeout:
        c_soc.close()
        return

    option = input("Choose number (1 or 2): ")  # get data from user
    while not option.isdigit() or (int(option) > 2 or int(option) < 1):
        option = input("Choose number (1 or 2): ")
    c_soc.send(option.encode())  # send to server

    chooseRounds(c_soc)


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # start the connection - tcp
    client_socket.connect((IP, PORT))  # connect to ip and port
    chooseTheGame(client_socket)  # start the game


if __name__ == '__main__':
    main()
