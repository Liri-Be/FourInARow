import json
import socket
from time import sleep

IP = "127.0.0.1"
PORT = 10000


def playTheGame(c_soc):
    """
    Handles the process of the game, from the client side
    :param c_soc: The socket for connection to server
    :return None:
    """
    finish = False
    while not finish:
        try:
            data_from_server = c_soc.recv(1024).decode()
            if "won!" in data_from_server:  # Win
                print(data_from_server)
                sleep(0.2)
                finish = True

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

    chooseTheGame(c_soc)  # return to main "screen"


def chooseTheGame(c_soc):
    """
    Handles the process of choosing whether the users wants to play
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

    playTheGame(c_soc)


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # start the connection - tcp
    client_socket.connect((IP, PORT))  # connect to ip and port
    chooseTheGame(client_socket)  # start the game


if __name__ == '__main__':
    main()
